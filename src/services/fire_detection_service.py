"""Service API for the improved one-class fire detector."""

from __future__ import annotations

from pathlib import Path

from config import DL_MODEL_DIR
from src.dl.predict import predict_fire


FIRE_MODEL_PATH = DL_MODEL_DIR / "crime_x_fire_detector_v2.pt"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def detect_fire(
    image_path: str | Path,
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.30,
    max_detections: int = 15,
) -> dict[str, object]:
    """Validate an image path and run v2 fire detection."""

    path = Path(image_path)
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image type; use JPG, JPEG, or PNG")
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    if not FIRE_MODEL_PATH.is_file():
        raise FileNotFoundError(f"Fire detector model not found: {FIRE_MODEL_PATH}")
    try:
        result = predict_fire(
            path,
            confidence_threshold=confidence_threshold,
            model_path=FIRE_MODEL_PATH,
            iou_threshold=iou_threshold,
            max_detections=max_detections,
        )
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Fire detection failed: {error}") from error
    return {"module": "fire_detection", "confidence_threshold": confidence_threshold, **result}