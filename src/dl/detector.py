"""YOLO fire detector loading and structured inference."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from ultralytics import YOLO


def compute_iou(box1: list[float], box2: list[float]) -> float:
    """Compute Intersection over Union between two bounding boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter_area = inter_w * inter_h
    box1_area = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    box2_area = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def apply_nms(
    detections: list[dict[str, object]],
    iou_threshold: float = 0.30,
    max_detections: int = 15,
) -> list[dict[str, object]]:
    """Deduplicate overlapping fire bounding boxes, keeping highest-confidence detections."""
    if not detections:
        return []
    sorted_dets = sorted(detections, key=lambda d: float(d["confidence"]), reverse=True)
    kept: list[dict[str, object]] = []
    for d in sorted_dets:
        box = d["bbox"]
        if not any(compute_iou(box, k["bbox"]) > iou_threshold for k in kept):
            kept.append(d)
        if len(kept) >= max_detections:
            break
    return kept


class FireDetector:
    """Load a trained one-class fire detector and return structured detections."""

    def __init__(self, model_path: Path):
        if not model_path.is_file():
            raise FileNotFoundError(f"Detector model not found: {model_path}")
        self.model = YOLO(str(model_path))

    def predict(
        self,
        image_path: Path,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.30,
        max_detections: int = 15,
    ) -> dict[str, object]:
        """Run inference on one real image with NMS deduplication to avoid overlapping boxes."""

        with Image.open(image_path) as image:
            width, height = image.size
        results = self.model.predict(
            str(image_path),
            conf=confidence_threshold,
            iou=iou_threshold,
            verbose=False,
        )
        raw_detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box, confidence, class_id in zip(boxes.xyxy.tolist(), boxes.conf.tolist(), boxes.cls.tolist()):
                raw_detections.append({
                    "class": str(self.model.names[int(class_id)]),
                    "confidence": float(confidence),
                    "bbox": [float(value) for value in box],
                })
        detections = apply_nms(raw_detections, iou_threshold=iou_threshold, max_detections=max_detections)
        return {"detections": detections, "image_width": width, "image_height": height}