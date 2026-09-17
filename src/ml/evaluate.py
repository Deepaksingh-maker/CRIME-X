"""Evaluation helpers for the limited academic ML experiment."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    """Calculate standard regression metrics for a held-out set."""

    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(actual, predicted)),
    }


def compare_models(
    models: dict[str, object],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    """Fit and compare models on one fixed, non-random holdout."""

    rows = []
    for name, model in models.items():
        model.fit(x_train, y_train)
        metrics = regression_metrics(y_test, model.predict(x_test))
        rows.append({
            "model": name,
            **metrics,
            "train_rows": len(x_train),
            "validation_rows": len(x_test),
            "validation_method": "deterministic state holdout; not temporal",
        })
    return pd.DataFrame(rows).sort_values(["RMSE", "MAE"], ascending=True).reset_index(drop=True)