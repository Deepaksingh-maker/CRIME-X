from pathlib import Path

import pandas as pd

from src.ml.predict import predict_count
from src.ml.train import (
    BEST_MODEL_PATH,
    MODEL_COMPARISON_PATH,
    TRAINING_DATASET_PATH,
    train_and_evaluate,
)


def test_training_creates_real_artifacts():
    comparison, artifact = train_and_evaluate()
    assert len(comparison) == 4
    assert set(comparison["model"]) == {
        "BaselineMean",
        "LinearRegression",
        "RandomForestRegressor",
        "HistGradientBoostingRegressor",
    }
    assert artifact["confidence"] is None
    assert BEST_MODEL_PATH.is_file()
    assert MODEL_COMPARISON_PATH.is_file()
    assert TRAINING_DATASET_PATH.is_file()


def test_prediction_returns_structured_limited_data_warning():
    train_and_evaluate()
    result = predict_count({
        "lag_2020_count": 100,
        "lag_2021_count": 90,
        "population_2022_lakhs": 500,
    })
    assert set(result) == {"predicted_count", "model", "confidence", "warning"}
    assert result["predicted_count"] >= 0
    assert result["confidence"] is None
    assert "Limited historical data" in result["warning"]


def test_comparison_contains_numeric_metrics():
    comparison, _ = train_and_evaluate()
    assert comparison[["MAE", "RMSE", "R2"]].map(pd.api.types.is_number).all().all()