"""Train and evaluate CRIME X's academic regression experiment."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from config import ML_MODEL_DIR, PROCESSED_DIR
from .evaluate import compare_models, regression_metrics
from .features import build_selected_state_features
from .preprocess import FEATURE_COLUMNS, TARGET_COLUMN, chronological_split, prepare_regression_data


BEST_MODEL_PATH = ML_MODEL_DIR / "best_model.joblib"
MODEL_COMPARISON_PATH = ML_MODEL_DIR / "model_comparison.csv"
TRAINING_DATASET_PATH = PROCESSED_DIR / "ml_training_dataset.csv"

LIMITATION_WARNING = "Limited historical data: academic decision-support experiment, not a production forecast."


def build_training_dataset(output_path: Path = TRAINING_DATASET_PATH) -> pd.DataFrame:
    """Create the final real-data training table."""

    dataframe = build_selected_state_features()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")
    return dataframe


def _build_models() -> dict[str, object]:
    return {
        "BaselineMean": None,
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            min_samples_leaf=2,
        ),
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(
            max_iter=100,
            learning_rate=0.05,
            max_leaf_nodes=8,
            l2_regularization=1.0,
            random_state=42,
        ),
    }


def train_and_evaluate() -> tuple[pd.DataFrame, dict[str, object]]:
    """Evaluate candidates, select by validation RMSE, and save the full-data winner."""

    dataframe = build_training_dataset()
    x_data, target = prepare_regression_data(dataframe)
    train_frame, validation_frame = chronological_split(dataframe)
    x_train, y_train = prepare_regression_data(train_frame)
    x_validation, y_validation = prepare_regression_data(validation_frame)

    models = _build_models()
    comparison_rows = []
    baseline_value = float(y_train.mean())
    baseline_prediction = np.full(len(y_validation), baseline_value)
    comparison_rows.append({
        "model": "BaselineMean",
        **regression_metrics(y_validation, baseline_prediction),
        "train_rows": len(x_train),
        "validation_rows": len(x_validation),
        "validation_method": "deterministic state holdout; not temporal",
    })

    fitted_candidates = compare_models(
        {name: model for name, model in models.items() if model is not None},
        x_train,
        y_train,
        x_validation,
        y_validation,
    )
    comparison = pd.concat([pd.DataFrame(comparison_rows), fitted_candidates], ignore_index=True)
    comparison = comparison.sort_values(["RMSE", "MAE"], ascending=True).reset_index(drop=True)
    best_name = str(comparison.iloc[0]["model"])

    if best_name == "BaselineMean":
        best_estimator = {"type": "mean", "value": float(target.mean())}
    else:
        best_estimator = _build_models()[best_name]
        best_estimator.fit(x_data, target)

    artifact = {
        "model": best_estimator,
        "model_name": best_name,
        "feature_columns": list(FEATURE_COLUMNS),
        "target_column": TARGET_COLUMN,
        "training_rows": len(dataframe),
        "validation_method": "deterministic state holdout; not temporal",
        "warning": LIMITATION_WARNING,
        "confidence": None,
    }
    ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, BEST_MODEL_PATH)
    comparison.to_csv(MODEL_COMPARISON_PATH, index=False, encoding="utf-8-sig")
    return comparison, artifact


if __name__ == "__main__":
    results, artifact = train_and_evaluate()
    print(results.to_string(index=False))
    print(f"Best model: {artifact['model_name']}")