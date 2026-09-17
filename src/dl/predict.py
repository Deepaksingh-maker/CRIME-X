"""Public prediction function for the trained fire detector."""

from __future__ import annotations

from pathlib import Path

from config import DL_MODEL_DIR
from .detector import FireDetector


MODEL_PATH = DL_MODEL_DIR / "crime_x_fire_detector.pt"


def predict_fire(
    image_path: Path,
    confidence_threshold: float = 0.25,
    model_path: Path = MODEL_PATH,
    iou_threshold: float = 0.30,
    max_detections: int = 15,
) -> dict[str, object]:
    """Return fire detections and source image dimensions."""

    return FireDetector(model_path).predict(
        image_path,
        confidence_threshold=confidence_threshold,
        iou_threshold=iou_threshold,
        max_detections=max_detections,
    )