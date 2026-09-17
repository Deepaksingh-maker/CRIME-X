import json
from pathlib import Path

import pandas as pd


def test_v2_artifacts_and_comparison_exist_after_training():
    model = Path("models/dl/crime_x_fire_detector_v2.pt")
    comparison = Path("models/dl/model_comparison.csv")
    metrics = Path("models/dl/model_metrics_v2.json")
    inference = Path("models/dl/v2_inference_report.csv")
    predictions = Path("models/dl/predictions")
    assert model.is_file()
    assert comparison.is_file()
    assert metrics.is_file()
    assert inference.is_file()
    assert predictions.is_dir()
    table = pd.read_csv(comparison)
    assert table["model"].tolist() == ["v1", "v2"]
    assert json.loads(metrics.read_text(encoding="utf-8"))["class_names"] == ["fire"]
    assert len(pd.read_csv(inference)) == 10