"""
Temporary ML dataset builder for EventFlow AI.

Purpose
-------
Reads crowd_state from the existing PostgreSQL database and prepares a
clean, time-aware supervised-learning dataset for crowd prediction.

Important:
- This file NEVER modifies the database.
- Duplicate observations are removed IN MEMORY only.
- Existing database schema is not changed.
- Simulated/demo data remains explicitly identifiable through data_status.
- Targets are future crowd counts, not the seeded predictions table.

Expected environment
--------------------
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

Example:
    python app/ml/dataset_builder.py

The resulting CSV is written to:
    data/ml/crowd_prediction_dataset.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_HORIZONS = (10, 20, 30)
DEFAULT_TARGET_TOLERANCE_MINUTES = 10

REQUIRED_COLUMNS = {
    "event_id",
    "zone_id",
    "current_count",
    "inflow_rate",
    "outflow_rate",
    "density",
    "load_percentage",
    "timestamp",
}


# ---------------------------------------------------------------------------
# Database loading
# ---------------------------------------------------------------------------

def load_crowd_state(database_url: str) -> pd.DataFrame:
    """Load crowd observations from the existing crowd_state table."""
    engine = create_engine(database_url, pool_pre_ping=True)

    query = text(
        """
        SELECT
            event_id,
            zone_id,
            current_count,
            inflow_rate,
            outflow_rate,
            density,
            load_percentage,
            timestamp,
            data_status
        FROM crowd_state
        WHERE timestamp IS NOT NULL
        ORDER BY zone_id, timestamp, crowd_state_id
        """
    )

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    engine.dispose()

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"crowd_state is missing required columns: {sorted(missing)}"
        )

    return df


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_crowd_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean observations without changing the source database.

    Duplicate definition:
        event_id + zone_id + timestamp

    If duplicates exist, the first database row is retained. The database
    teammate can later remove duplicates permanently; this ML layer remains
    safe in the meantime.
    """
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    numeric_columns = [
        "current_count",
        "inflow_rate",
        "outflow_rate",
        "density",
        "load_percentage",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before = len(df)

    df = df.dropna(
        subset=[
            "event_id",
            "zone_id",
            "timestamp",
            "current_count",
            "inflow_rate",
            "outflow_rate",
            "density",
            "load_percentage",
        ]
    )

    # Remove impossible negative operational values.
    valid_mask = (
        (df["current_count"] >= 0)
        & (df["inflow_rate"] >= 0)
        & (df["outflow_rate"] >= 0)
        & (df["density"] >= 0)
    )
    df = df.loc[valid_mask].copy()

    # Remove accidental duplicate observations in memory.
    df = (
        df.sort_values(["event_id", "zone_id", "timestamp"])
        .drop_duplicates(
            subset=["event_id", "zone_id", "timestamp"],
            keep="first",
        )
        .reset_index(drop=True)
    )

    removed = before - len(df)

    print(f"[dataset_builder] Rows before cleaning: {before}")
    print(f"[dataset_builder] Rows after cleaning:  {len(df)}")
    print(f"[dataset_builder] Rows removed in memory: {removed}")

    return df


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar/event-time features without using future information."""
    df = df.copy()

    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df["minutes_from_midnight"] = df["hour"] * 60 + df["minute"]

    # Cyclic encoding avoids treating 23:59 and 00:00 as far apart.
    minutes = df["minutes_from_midnight"]
    df["time_sin"] = np.sin(2 * np.pi * minutes / 1440)
    df["time_cos"] = np.cos(2 * np.pi * minutes / 1440)

    return df


def add_history_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features using only current/past observations within each zone.

    The source data is ordered chronologically before rolling/lag operations.
    """
    df = df.copy()
    group = df.groupby(["event_id", "zone_id"], sort=False)

    df["count_lag_1"] = group["current_count"].shift(1)
    df["count_lag_2"] = group["current_count"].shift(2)

    df["load_lag_1"] = group["load_percentage"].shift(1)
    df["load_lag_2"] = group["load_percentage"].shift(2)

    df["count_change_1"] = (
        df["current_count"] - df["count_lag_1"]
    )
    df["count_change_2"] = (
        df["current_count"] - df["count_lag_2"]
    )

    df["load_change_1"] = (
        df["load_percentage"] - df["load_lag_1"]
    )

    # Rolling statistics use only the current row and previous rows.
    df["count_rolling_mean_3"] = (
        group["current_count"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    df["count_rolling_std_3"] = (
        group["current_count"]
        .transform(lambda s: s.rolling(window=3, min_periods=2).std())
        .fillna(0)
    )

    return df


# ---------------------------------------------------------------------------
# Future target creation
def add_future_targets(
    df: pd.DataFrame,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    tolerance_minutes: int = DEFAULT_TARGET_TOLERANCE_MINUTES,
) -> pd.DataFrame:
    """
    Add future crowd-count targets.

    For each observation at time T, find the first observation at or after:

        T + horizon

    The observation must be within tolerance_minutes of the requested
    target time. No interpolation or fabricated values are used.
    """

    base = df.copy()
    result = base.copy()

    tolerance = pd.Timedelta(minutes=tolerance_minutes)

    for horizon in horizons:
        target_column = f"target_count_{horizon}m"
        target_time_column = f"target_timestamp_{horizon}m"

        target_parts = []

        for (event_id, zone_id), group in base.groupby(
            ["event_id", "zone_id"],
            sort=False,
        ):
            group = group.sort_values("timestamp").copy()

            current = group[
                ["event_id", "zone_id", "timestamp"]
            ].copy()

            current["desired_target_time"] = (
                current["timestamp"]
                + pd.Timedelta(minutes=horizon)
            )

            future = group[
                ["timestamp", "current_count"]
            ].copy()

            future = future.rename(
                columns={
                    "timestamp": "future_timestamp",
                    "current_count": target_column,
                }
            )

            current = current.sort_values("desired_target_time")
            future = future.sort_values("future_timestamp")

            merged = pd.merge_asof(
                current,
                future,
                left_on="desired_target_time",
                right_on="future_timestamp",
                direction="forward",
                tolerance=tolerance,
            )

            invalid_future = (
                merged["future_timestamp"].isna()
                | (
                    merged["future_timestamp"]
                    < merged["desired_target_time"]
                )
            )

            merged.loc[invalid_future, target_column] = np.nan
            merged.loc[invalid_future, "future_timestamp"] = pd.NaT

            merged[target_time_column] = merged["future_timestamp"]

            target_parts.append(
                merged[
                    [
                        "event_id",
                        "zone_id",
                        "timestamp",
                        target_column,
                        target_time_column,
                    ]
                ]
            )

        target_frame = pd.concat(
            target_parts,
            ignore_index=True,
        )

        result = result.merge(
            target_frame,
            on=["event_id", "zone_id", "timestamp"],
            how="left",
        )

    return result
#---------------------------------------------------------------------------
# Complete dataset builder
# ---------------------------------------------------------------------------

def build_dataset(
    database_url: str,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    target_tolerance_minutes: int = DEFAULT_TARGET_TOLERANCE_MINUTES,
) -> pd.DataFrame:
    """Build the complete training dataset."""
    raw = load_crowd_state(database_url)
    clean = clean_crowd_state(raw)

    clean = clean.sort_values(
        ["event_id", "zone_id", "timestamp"]
    ).reset_index(drop=True)

    clean = add_time_features(clean)
    clean = add_history_features(clean)
    clean = add_future_targets(
        clean,
        horizons=horizons,
        tolerance_minutes=target_tolerance_minutes,
    )

    # Keep only rows with enough history and at least one future target.
    feature_columns = [
        "count_lag_1",
        "count_lag_2",
        "load_lag_1",
        "load_lag_2",
    ]

    clean = clean.dropna(subset=feature_columns).copy()

    target_columns = [
        f"target_count_{h}m"
        for h in horizons
    ]

    clean = clean.dropna(
        subset=target_columns,
        how="all",
    ).reset_index(drop=True)

    return clean


# ---------------------------------------------------------------------------
# Utility output
# ---------------------------------------------------------------------------

def save_dataset(
    df: pd.DataFrame,
    output_path: str = "data/ml/crowd_prediction_dataset.csv",
) -> Path:
    """Save the prepared dataset locally."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    print(f"[dataset_builder] Dataset saved to: {path}")
    print(f"[dataset_builder] Final rows: {len(df)}")
    print(f"[dataset_builder] Final columns: {len(df.columns)}")

    return path


def summarize_dataset(df: pd.DataFrame) -> None:
    """Print a compact dataset audit."""
    print("\n=== EventFlow ML Dataset Summary ===")
    print(f"Rows: {len(df)}")
    print(f"Zones: {df['zone_id'].nunique()}")
    print(
        f"Time range: "
        f"{df['timestamp'].min()} -> {df['timestamp'].max()}"
    )

    if "data_status" in df.columns:
        print("\nData status:")
        print(df["data_status"].value_counts(dropna=False))

    print("\nRows per zone:")
    print(df.groupby("zone_id").size())

    print("\nTarget availability:")
    for horizon in DEFAULT_HORIZONS:
        column = f"target_count_{horizon}m"
        if column in df.columns:
            print(
                f"{column}: "
                f"{df[column].notna().sum()} rows"
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise SystemExit(
            "DATABASE_URL is not configured. "
            "Set it in your .env file/environment before running."
        )

    dataset = build_dataset(database_url)
    summarize_dataset(dataset)
    save_dataset(dataset)

