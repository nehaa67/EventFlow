from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATASET_PATH = Path("data/ml/crowd_prediction_dataset.csv")
MODEL_DIR = Path("data/ml/models")

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

HORIZONS = {
    10: "target_count_10m",
    20: "target_count_20m",
    30: "target_count_30m",
}


def baseline_prediction(df, horizon):
    """
    Simple physics-inspired baseline:
    future crowd = current crowd + net rate * time
    """
    net_rate = df["inflow_rate"] - df["outflow_rate"]

    return np.maximum(
        0,
        df["current_count"] + net_rate * horizon,
    )


def evaluate_model(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": rmse,
        "R2": r2_score(y_true, y_pred),
    }


def train_horizon(df, horizon, target_column):
    print(f"\n{'=' * 60}")
    print(f"Training {horizon}-minute model")
    print(f"{'=' * 60}")

    data = df.dropna(subset=FEATURES + [target_column]).copy()

    data = data.sort_values("timestamp")

    # Chronological split.
    # Earlier observations = training.
    # Later observations = validation.
    unique_times = sorted(data["timestamp"].unique())

    split_index = int(len(unique_times) * 0.8)

    if split_index <= 0 or split_index >= len(unique_times):
        raise ValueError("Not enough timestamps for chronological split.")

    split_time = unique_times[split_index]

    train = data[data["timestamp"] < split_time]
    validation = data[data["timestamp"] >= split_time]

    if train.empty or validation.empty:
        raise ValueError("Training or validation set is empty.")

    X_train = train[FEATURES]
    y_train = train[target_column]

    X_val = validation[FEATURES]
    y_val = validation[target_column]

    print(f"Total samples : {len(data)}")
    print(f"Train samples : {len(train)}")
    print(f"Validation    : {len(validation)}")
    print(f"Split time    : {split_time}")

    # ---------------------------------------------------------
    # Baseline
    # ---------------------------------------------------------

    baseline_pred = baseline_prediction(validation, horizon)
    baseline_metrics = evaluate_model(y_val, baseline_pred)

    print("\nBaseline:")
    print(f"  MAE  : {baseline_metrics['MAE']:.2f}")
    print(f"  RMSE : {baseline_metrics['RMSE']:.2f}")
    print(f"  R²   : {baseline_metrics['R2']:.4f}")

    # ---------------------------------------------------------
    # Gradient Boosting
    # ---------------------------------------------------------

    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        random_state=42,
        loss="squared_error",
    )

    model.fit(X_train, y_train)

    ml_pred = model.predict(X_val)
    ml_pred = np.maximum(0, ml_pred)

    ml_metrics = evaluate_model(y_val, ml_pred)

    print("\nGradient Boosting:")
    print(f"  MAE  : {ml_metrics['MAE']:.2f}")
    print(f"  RMSE : {ml_metrics['RMSE']:.2f}")
    print(f"  R²   : {ml_metrics['R2']:.4f}")

    # ---------------------------------------------------------
    # Comparison
    # ---------------------------------------------------------

    print("\nComparison:")

    mae_improvement = (
        (baseline_metrics["MAE"] - ml_metrics["MAE"])
        / baseline_metrics["MAE"]
        * 100
        if baseline_metrics["MAE"] != 0
        else 0
    )

    print(f"  MAE improvement: {mae_improvement:.2f}%")

    if ml_metrics["MAE"] < baseline_metrics["MAE"]:
        print("  RESULT: ML beats baseline")
        winner = "gradient_boosting"
    else:
        print("  RESULT: Baseline beats or matches ML")
        winner = "baseline"

    # ---------------------------------------------------------
    # Save model
    # ---------------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / f"crowd_model_{horizon}m.joblib"

    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
            "horizon_minutes": horizon,
            "winner_on_validation": winner,
            "baseline_metrics": baseline_metrics,
            "ml_metrics": ml_metrics,
        },
        model_path,
    )

    print(f"\nModel saved: {model_path}")

    return {
        "horizon": horizon,
        "samples": len(data),
        "train_samples": len(train),
        "validation_samples": len(validation),
        "baseline": baseline_metrics,
        "gradient_boosting": ml_metrics,
        "winner": winner,
    }


def main():
    print("EventFlow AI - Crowd Prediction Training")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    print(f"\nDataset loaded: {DATASET_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Zones: {df['zone_id'].nunique()}")

    results = []

    for horizon, target_column in HORIZONS.items():
        result = train_horizon(
            df,
            horizon,
            target_column,
        )

        results.append(result)

    print("\n")
    print("=" * 60)
    print("FINAL TRAINING SUMMARY")
    print("=" * 60)

    for result in results:
        print(
            f"\n{result['horizon']} minutes:"
        )

        print(
            f"  Baseline MAE: "
            f"{result['baseline']['MAE']:.2f}"
        )

        print(
            f"  ML MAE: "
            f"{result['gradient_boosting']['MAE']:.2f}"
        )

        print(
            f"  Winner: "
            f"{result['winner']}"
        )


if __name__ == "__main__":
    main()