"""Structured prediction interface for the saved academic model."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .preprocess import FEATURE_COLUMNS
from .train import BEST_MODEL_PATH, LIMITATION_WARNING


def load_model(model_path: Path = BEST_MODEL_PATH) -> dict[str, object]:
    """Load the saved model artifact and its feature contract."""

    if not model_path.is_file():
        raise FileNotFoundError(f"Trained model not found: {model_path}")
    return joblib.load(model_path)


def predict_count(features: dict[str, float] | pd.DataFrame, model_path: Path = BEST_MODEL_PATH) -> dict[str, object]:
    """Return a labeled count estimate with no fabricated confidence value."""

    artifact = load_model(model_path)
    if isinstance(features, dict):
        dataframe = pd.DataFrame([features])
    else:
        dataframe = features.copy()
    missing = [column for column in FEATURE_COLUMNS if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing prediction features: {', '.join(missing)}")
    numeric_features = dataframe[list(FEATURE_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    if numeric_features.isna().any().any():
        raise ValueError("Prediction features must contain valid numeric values")
    model = artifact["model"]
    if isinstance(model, dict) and model.get("type") == "mean":
        prediction = float(model["value"])
    else:
        prediction = float(model.predict(numeric_features)[0])
    return {
        "predicted_count": max(0.0, prediction),
        "model": artifact["model_name"],
        "confidence": None,
        "warning": LIMITATION_WARNING,
    }