"""Preprocessing helpers for the selected ML feature table."""

from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = ("lag_2020_count", "lag_2021_count", "population_2022_lakhs")
TARGET_COLUMN = "target_count"


def prepare_regression_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return numeric features and target without fitting or imputing silently."""

    required = ["state_ut", *FEATURE_COLUMNS, TARGET_COLUMN]
    missing = sorted(set(required) - set(dataframe.columns))
    if missing:
        raise ValueError(f"Missing ML preprocessing columns: {', '.join(missing)}")
    working = dataframe[required].copy()
    working[list(FEATURE_COLUMNS) + [TARGET_COLUMN]] = working[list(FEATURE_COLUMNS) + [TARGET_COLUMN]].apply(
        pd.to_numeric, errors="coerce"
    )
    working = working.dropna(subset=[*FEATURE_COLUMNS, TARGET_COLUMN]).reset_index(drop=True)
    return working[list(FEATURE_COLUMNS)], working[TARGET_COLUMN]


def chronological_split(
    dataframe: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
    train_fraction: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split rows in source order; this is a guardrail, not random shuffling."""

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    if target_column not in dataframe.columns:
        raise ValueError(f"Target column not found: {target_column}")
    split_index = max(1, min(len(dataframe) - 1, int(len(dataframe) * train_fraction)))
    return dataframe.iloc[:split_index].copy(), dataframe.iloc[split_index:].copy()