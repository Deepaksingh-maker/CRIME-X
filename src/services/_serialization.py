"""Helpers for converting analytics results into JSON-compatible values."""

from __future__ import annotations

from typing import Any

import pandas as pd


def to_jsonable(value: Any) -> Any:
    """Convert pandas/numpy values and nested analytics results to plain Python."""

    if isinstance(value, pd.DataFrame):
        return [to_jsonable(record) for record in value.to_dict(orient="records")]
    if isinstance(value, pd.Series):
        return [to_jsonable(item) for item in value.tolist()]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items() if key != "source"}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value