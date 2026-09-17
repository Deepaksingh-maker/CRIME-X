"""Evaluation and result recording for the trained fire detector."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from ultralytics import YOLO

from config import DL_MODEL_DIR
from .dataset_inspection import YOLO_OUTPUT_ROOT
from .predict import predict_fire


METRICS_PATH = DL_MODEL_DIR / "model_metrics.json"
RESULTS_PATH = DL_MODEL_DIR / "training_results.csv"


def _metric(metrics: Any, name: str) -> float | None:
    value = getattr(metrics.box, name, None)
    return float(value) if value is not None else None


def evaluate_model(model_path: Path, data_yaml: Path = YOLO_OUTPUT_ROOT / "dataset.yaml") -> dict[str, object]:
    """Evaluate a trained model on the held-out test split."""

    model = YOLO(str(model_path))
    validation = model.val(data=str(data_yaml), split="test", imgsz=640, verbose=False)
    return {
        "precision": _metric(validation, "mp"),
        "recall": _metric(validation, "mr"),
        "mAP50": _metric(validation, "map50"),
        "mAP50-95": _metric(validation, "map"),
        "false_positives": None,
        "false_negatives": None,
        "test_evaluation_note": "False-positive and false-negative counts are not exposed as stable scalar values by this evaluation API.",
    }


def run_test_inference(model_path: Path, data_yaml: Path = YOLO_OUTPUT_ROOT / "dataset.yaml") -> list[dict[str, object]]:
    """Run inference on every test image and return structured outputs."""

    test_dir = YOLO_OUTPUT_ROOT / "images" / "test"
    return [{"image": str(path), **predict_fire(path, model_path=model_path)} for path in sorted(test_dir.glob("*.jpg"))]


def save_evaluation(
    metrics: dict[str, object],
    inference_results: list[dict[str, object]],
    configuration: dict[str, object],
    metrics_path: Path = METRICS_PATH,
    results_path: Path = RESULTS_PATH,
) -> None:
    """Persist metrics JSON and one row per test inference."""

    DL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    payload = {**configuration, "metrics": metrics, "test_inference_count": len(inference_results)}
    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    rows = []
    for result in inference_results:
        rows.append({
            "image": result["image"],
            "detections": len(result["detections"]),
            "confidence": max((item["confidence"] for item in result["detections"]), default=None),
            "number_of_detections": len(result["detections"]),
            "detected_classes": ";".join(sorted({item["class"] for item in result["detections"]})),
        })
    pd.DataFrame(rows).to_csv(results_path, index=False, encoding="utf-8-sig")