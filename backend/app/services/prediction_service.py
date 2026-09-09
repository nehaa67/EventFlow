from pathlib import Path
from datetime import datetime
import math

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.models import CrowdState


# -------------------------------------------------------------------
# Model configuration
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "data" / "ml" / "models"

MODEL_PATHS = {
    10: MODEL_DIR / "crowd_model_10m.joblib",
    20: MODEL_DIR / "crowd_model_20m.joblib",
    30: MODEL_DIR / "crowd_model_30m.joblib",
}

FEATURES = [
    "current_count",
    "inflow_rate",
    "outflow_rate",
    "density",
    "load_percentage",
    "count_lag_1",
    "count_lag_2",
    "load_lag_1",
    "load_lag_2",
    "count_change_1",
    "count_change_2",
    "load_change_1",
    "count_rolling_mean_3",
    "count_rolling_std_3",
    "time_sin",
    "time_cos",
]


# -------------------------------------------------------------------
# Load trained models
# -------------------------------------------------------------------

MODELS = {}

for horizon, path in MODEL_PATHS.items():
    if path.exists():
        artifact = joblib.load(path)

        if isinstance(artifact, dict) and "model" in artifact:
            MODELS[horizon] = artifact["model"]
        else:
            MODELS[horizon] = artifact


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def _safe_float(value, default=0.0):
    """Convert a value to float safely."""

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _time_features(timestamp: datetime):
    """Create the same cyclic time features used during training."""

    if timestamp is None:
        return 0.0, 0.0

    minutes_from_midnight = (
        timestamp.hour * 60
        + timestamp.minute
        + timestamp.second / 60
    )

    angle = (
        2 * math.pi * minutes_from_midnight / 1440
    )

    return math.sin(angle), math.cos(angle)


def _build_features_from_history(history: list[CrowdState]):
    """
    Build ML features from historical crowd_state observations.

    history must be ordered oldest -> newest.
    The final observation represents the current state.
    """

    if not history:
        raise ValueError("No crowd history available.")

    rows = []

    for row in history:
        rows.append(
            {
                "current_count": _safe_float(row.current_count),
                "inflow_rate": _safe_float(row.inflow_rate),
                "outflow_rate": _safe_float(row.outflow_rate),
                "density": _safe_float(row.density),
                "load_percentage": _safe_float(row.load_percentage),
                "timestamp": row.recorded_at,
            }
        )

    df = pd.DataFrame(rows)

    # ---------------------------------------------------------------
    # Same historical features used by dataset_builder.py
    # ---------------------------------------------------------------

    df["count_lag_1"] = df["current_count"].shift(1)
    df["count_lag_2"] = df["current_count"].shift(2)

    df["load_lag_1"] = df["load_percentage"].shift(1)
    df["load_lag_2"] = df["load_percentage"].shift(2)

    df["count_change_1"] = (
        df["current_count"]
        - df["count_lag_1"]
    )

    df["count_change_2"] = (
        df["current_count"]
        - df["count_lag_2"]
    )

    df["load_change_1"] = (
        df["load_percentage"]
        - df["load_lag_1"]
    )

    df["count_rolling_mean_3"] = (
        df["current_count"]
        .rolling(window=3)
        .mean()
    )

    df["count_rolling_std_3"] = (
        df["current_count"]
        .rolling(window=3)
        .std()
    )

    # Cyclic time features
    time_features = df["timestamp"].apply(
        _time_features
    )

    df["time_sin"] = time_features.apply(
        lambda x: x[0]
    )

    df["time_cos"] = time_features.apply(
        lambda x: x[1]
    )

    # The latest observation is the prediction input.
    latest = df.iloc[-1]

    # ---------------------------------------------------------------
    # If history is insufficient, fail explicitly instead of silently
    # fabricating historical values.
    # ---------------------------------------------------------------

    required_history_columns = [
        "count_lag_1",
        "count_lag_2",
        "load_lag_1",
        "load_lag_2",
        "count_change_1",
        "count_change_2",
        "load_change_1",
        "count_rolling_mean_3",
        "count_rolling_std_3",
    ]

    for column in required_history_columns:
        if pd.isna(latest[column]):
            raise ValueError(
                "Insufficient crowd history to build "
                f"ML features: {column}"
            )

    feature_values = {
        feature: _safe_float(latest[feature])
        for feature in FEATURES
    }

    return feature_values


def _baseline_prediction(
    current_count: float,
    arrival_rate: float,
    departure_rate: float,
    minutes: int,
) -> float:

    net_rate = arrival_rate - departure_rate

    future_count = (
        current_count
        + (net_rate * minutes)
    )

    return max(0.0, future_count)


# -------------------------------------------------------------------
# Get historical crowd state
# -------------------------------------------------------------------

def _get_crowd_history(
    db: Session,
    event_id: int,
    zone_id: int,
    limit: int = 10,
):
    """
    Retrieve recent crowd observations for one event + zone.

    We retrieve a few more than the minimum required so the feature
    calculation has enough history.
    """

    rows = (
        db.query(CrowdState)
        .filter(
            CrowdState.event_id == event_id,
            CrowdState.zone_id == zone_id,
        )
        .order_by(
            CrowdState.recorded_at.desc()
        )
        .limit(limit)
        .all()
    )

    # Query is newest -> oldest.
    # Feature engineering requires oldest -> newest.
    rows.reverse()

    return rows


# -------------------------------------------------------------------
# Main prediction function
# -------------------------------------------------------------------

def predict_crowd_growth(
    db: Session,
    event_id: int,
    zone_id: int,
    capacity: float,
    horizons: list[int] | None = None,
):
    """
    Predict future crowd count using trained ML models.

    Historical features are calculated directly from crowd_state.

    ML predictions are compared against the transparent
    rate-based baseline.
    """

    if horizons is None:
        horizons = [10, 20, 30]

    if not horizons:
        raise ValueError(
            "At least one prediction horizon is required."
        )

    capacity = _safe_float(capacity)

    if capacity <= 0:
        raise ValueError(
            f"Invalid capacity for zone {zone_id}: {capacity}"
        )

    # ---------------------------------------------------------------
    # Retrieve real database history
    # ---------------------------------------------------------------

    history = _get_crowd_history(
        db=db,
        event_id=event_id,
        zone_id=zone_id,
        limit=10,
    )

    if not history:
        raise ValueError(
            f"No crowd_state history found for "
            f"event {event_id}, zone {zone_id}."
        )

    # ---------------------------------------------------------------
    # Build features from actual history
    # ---------------------------------------------------------------

    feature_values = _build_features_from_history(
        history
    )

    feature_frame = pd.DataFrame(
        [feature_values],
        columns=FEATURES,
    )

    # Current values come from the latest DB observation.
    latest = history[-1]

    current_count = _safe_float(
        latest.current_count
    )

    arrival_rate = _safe_float(
        latest.inflow_rate
    )

    departure_rate = _safe_float(
        latest.outflow_rate
    )

    # ---------------------------------------------------------------
    # Generate predictions
    # ---------------------------------------------------------------

    predictions = {}

    for minutes in horizons:

        baseline_count = _baseline_prediction(
            current_count=current_count,
            arrival_rate=arrival_rate,
            departure_rate=departure_rate,
            minutes=minutes,
        )

        model = MODELS.get(minutes)

        if model is not None:

            ml_count = float(
                model.predict(feature_frame)[0]
            )

            ml_count = max(
                0.0,
                ml_count,
            )

            prediction_source = "ML"

        else:

            ml_count = baseline_count

            prediction_source = (
                "BASELINE_FALLBACK"
            )

        load_percentage = (
            ml_count / capacity
        ) * 100

        baseline_load_percentage = (
            baseline_count / capacity
        ) * 100

        predictions[minutes] = {
            "predicted_count": round(
                ml_count,
                2,
            ),
            "load_percentage": round(
                load_percentage,
                2,
            ),
            "baseline_count": round(
                baseline_count,
                2,
            ),
            "baseline_load_percentage": round(
                baseline_load_percentage,
                2,
            ),
            "prediction_source": prediction_source,
        }

    # ---------------------------------------------------------------
    # Capacity breach ETA
    # ---------------------------------------------------------------

    net_rate = (
        arrival_rate
        - departure_rate
    )

    breach_eta = None

    if current_count >= capacity:

        breach_eta = 0

    elif net_rate > 0:

        minutes_to_breach = (
            capacity - current_count
        ) / net_rate

        breach_eta = round(
            minutes_to_breach,
            2,
        )

    # ---------------------------------------------------------------
    # Hotspot determination
    # ---------------------------------------------------------------

    max_predicted_load = max(
        prediction["load_percentage"]
        for prediction in predictions.values()
    )

    hotspot = (
        max_predicted_load >= 90
    )

    # ---------------------------------------------------------------
    # Final response
    # ---------------------------------------------------------------

    return {
        "event_id": event_id,
        "zone_id": zone_id,
        "current_count": round(
            current_count,
            2,
        ),
        "capacity": round(
            capacity,
            2,
        ),
        "current_load_percentage": round(
            (
                current_count
                / capacity
            ) * 100,
            2,
        ),
        "history_points_used": len(history),
        "predictions": predictions,
        "breach_eta": breach_eta,
        "hotspot": hotspot,
        "max_predicted_load_percentage": round(
            max_predicted_load,
            2,
        ),
    }