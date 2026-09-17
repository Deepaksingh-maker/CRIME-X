"""Train the lightweight one-class YOLO fire detector."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
from ultralytics import YOLO

from config import DL_MODEL_DIR
from .dataset_inspection import YOLO_OUTPUT_ROOT, inspect_dataset, prepare_yolo_dataset
from .evaluate import evaluate_model, run_test_inference, save_evaluation


MODEL_PATH = DL_MODEL_DIR / "crime_x_fire_detector.pt"
V2_MODEL_PATH = DL_MODEL_DIR / "crime_x_fire_detector_v2.pt"
BASE_MODEL = "yolo11n.pt"


def verify_training_dataset() -> dict[str, object]:
    """Verify YAML, one class, split images, labels, and normalized boxes."""

    report = inspect_dataset().report.iloc[0]
    if report["status"] != "PASS":
        raise ValueError("Source DL dataset quality checks did not pass")
    if not (YOLO_OUTPUT_ROOT / "dataset.yaml").is_file():
        raise FileNotFoundError("Prepared YOLO dataset.yaml is missing")
    if report["classes"] != "fire":
        raise ValueError(f"Expected only fire class, found: {report['classes']}")
    split_counts = {}
    for split in ("train", "val", "test"):
        images = list((YOLO_OUTPUT_ROOT / "images" / split).glob("*.jpg"))
        labels = [(YOLO_OUTPUT_ROOT / "labels" / split / f"{image.stem}.txt") for image in images]
        if len(images) != len(labels) or not all(label.is_file() for label in labels):
            raise ValueError(f"Missing image/label pair in {split} split")
        split_counts[split] = len(images)
    return {"classes": ["fire"], "train_images": split_counts["train"], "validation_images": split_counts["val"], "test_images": split_counts["test"]}


def train_model(epochs: int = 2, image_size: int = 320) -> tuple[Path, dict[str, object]]:
    """Train, evaluate, and save the fire detector without overwriting a model."""

    configuration = verify_training_dataset()
    prepare_yolo_dataset(YOLO_OUTPUT_ROOT)
    DL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {MODEL_PATH}")
    model = YOLO(BASE_MODEL)
    results = model.train(
        data=str(YOLO_OUTPUT_ROOT / "dataset.yaml"),
        epochs=epochs,
        imgsz=image_size,
        batch=16,
        device="cpu",
        workers=0,
        seed=42,
        deterministic=True,
        project=str(DL_MODEL_DIR / "runs"),
        name="fire_detector_academic",
        exist_ok=False,
        verbose=False,
    )
    best_path = Path(results.save_dir) / "weights" / "best.pt"
    if not best_path.is_file():
        raise FileNotFoundError(f"Training did not produce best.pt: {best_path}")
    shutil.copy2(best_path, MODEL_PATH)
    metrics = evaluate_model(MODEL_PATH)
    inference_results = run_test_inference(MODEL_PATH)
    configuration.update({
        "model": BASE_MODEL,
        "saved_model": str(MODEL_PATH),
        "epochs": epochs,
        "image_size": image_size,
        "class_names": ["fire"],
        "limitation": "Only 100 images and one annotated class; not production-ready.",
    })
    save_evaluation(metrics, inference_results, configuration)
    return MODEL_PATH, {"configuration": configuration, "metrics": metrics, "test_inference": inference_results}


def _save_annotated_predictions(model_path: Path, output_dir: Path) -> None:
    """Save Ultralytics annotated predictions for all real test images."""

    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite prediction directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(model_path))
    model.predict(
        source=str(YOLO_OUTPUT_ROOT / "images" / "test"),
        conf=0.25,
        imgsz=320,
        save=True,
        project=str(output_dir.parent),
        name=output_dir.name,
        exist_ok=True,
        verbose=False,
    )


def train_improved_model(epochs: int = 8, image_size: int = 320) -> tuple[Path, dict[str, object]]:
    """Train v2 with bounded early stopping and compare it with v1."""

    configuration = verify_training_dataset()
    if V2_MODEL_PATH.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {V2_MODEL_PATH}")
    model = YOLO(BASE_MODEL)
    results = model.train(
        data=str(YOLO_OUTPUT_ROOT / "dataset.yaml"),
        epochs=epochs,
        imgsz=image_size,
        batch=16,
        device="cpu",
        workers=0,
        seed=42,
        deterministic=True,
        patience=3,
        close_mosaic=3,
        project=str(DL_MODEL_DIR / "runs"),
        name="fire_detector_v2",
        exist_ok=False,
        verbose=False,
    )
    best_path = Path(results.save_dir) / "weights" / "best.pt"
    if not best_path.is_file():
        raise FileNotFoundError(f"Training did not produce best.pt: {best_path}")
    shutil.copy2(best_path, V2_MODEL_PATH)
    metrics = evaluate_model(V2_MODEL_PATH)
    inference_results = run_test_inference(V2_MODEL_PATH)
    inference_path = DL_MODEL_DIR / "v2_inference_report.csv"
    metrics_path = DL_MODEL_DIR / "model_metrics_v2.json"
    configuration.update({
        "model": BASE_MODEL,
        "saved_model": str(V2_MODEL_PATH),
        "epochs": epochs,
        "image_size": image_size,
        "batch_size": 16,
        "patience": 3,
        "class_names": ["fire"],
        "limitation": "Only 100 images and one annotated class; not production-ready.",
    })
    save_evaluation(metrics, inference_results, configuration, metrics_path, inference_path)
    _save_annotated_predictions(V2_MODEL_PATH, DL_MODEL_DIR / "predictions")

    v1_metrics = json.loads((DL_MODEL_DIR / "model_metrics.json").read_text(encoding="utf-8"))["metrics"]
    comparison = pd.DataFrame([
        {"model": "v1", "model_file": str(MODEL_PATH), **{key: v1_metrics[key] for key in ("precision", "recall", "mAP50", "mAP50-95")}, "epochs": 2, "image_size": 320},
        {"model": "v2", "model_file": str(V2_MODEL_PATH), **{key: metrics[key] for key in ("precision", "recall", "mAP50", "mAP50-95")}, "epochs": epochs, "image_size": image_size},
    ])
    comparison.to_csv(DL_MODEL_DIR / "model_comparison.csv", index=False, encoding="utf-8-sig")
    return V2_MODEL_PATH, {"configuration": configuration, "metrics": metrics, "test_inference": inference_results}


if __name__ == "__main__":
    path, summary = train_improved_model()
    print(path)
    print(summary["metrics"])