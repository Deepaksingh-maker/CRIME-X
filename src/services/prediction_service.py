"""Service API for the academic crime-count prediction model."""

from __future__ import annotations

from typing import Mapping

from src.ml.predict import predict_count


REQUIRED_FEATURES = ("lag_2020_count", "lag_2021_count", "population_2022_lakhs")


def predict_crime_count(features: Mapping[str, float]) -> dict[str, object]:
    """Validate input and return a labeled decision-support prediction."""

    if not isinstance(features, Mapping):
        raise TypeError("Prediction input must be a mapping of feature names to values")
    missing = [name for name in REQUIRED_FEATURES if name not in features]
    if missing:
        raise ValueError(f"Missing prediction features: {', '.join(missing)}")
    try:
        result = predict_count(dict(features))
    except (FileNotFoundError, ValueError, TypeError) as error:
        raise RuntimeError(f"Crime prediction failed: {error}") from error
    return {"module": "crime_prediction", **result}