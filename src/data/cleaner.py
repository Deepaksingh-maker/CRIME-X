"""Conservative cleaning helpers for the project's source datasets."""

import re
from typing import Iterable

import pandas as pd


MISSING_MARKERS = {"", "-", "--", "na", "n/a", "nan", "null", "none"}


def normalize_column_name(column: object) -> str:
    """Normalize a column label while retaining meaningful words."""

    value = str(column).replace("\ufeff", "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value


def clean_dataframe(dataframe: pd.DataFrame, numeric_columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Return a cleaned copy without changing the raw input file."""

    cleaned = dataframe.copy()
    cleaned = cleaned.dropna(axis=0, how="all").dropna(axis=1, how="all")
    cleaned.columns = [normalize_column_name(column) for column in cleaned.columns]

    for column in cleaned.columns:
        cleaned[column] = cleaned[column].map(
            lambda value: (
                pd.NA
                if isinstance(value, str) and value.strip().lower() in MISSING_MARKERS
                else value.strip() if isinstance(value, str) else value
            )
        )

    requested_numeric = set(numeric_columns or ())
    inferred_numeric = {
        column
        for column in cleaned.columns
        if any(token in column for token in ("year", "number", "total", "count", "rate", "cases"))
    }
    for column in requested_numeric | inferred_numeric:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in ("state_ut", "state", "district", "city_name"):
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").str.strip()

    return cleaned