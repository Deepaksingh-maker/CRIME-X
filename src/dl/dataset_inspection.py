"""Inspection and safe Pascal VOC to YOLO preparation for the real DL dataset."""

from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps

from config import DATA_DIR, PROCESSED_DIR


DATASET_ROOT = DATA_DIR / "deep learning" / "India Fire & Smoke Dataset"
IMAGE_ROOT = DATASET_ROOT / "Datacluster Fire and Smoke Sample"
ANNOTATION_ROOT = DATASET_ROOT / "Annotations"
YOLO_OUTPUT_ROOT = PROCESSED_DIR / "dl_yolo"


@dataclass(frozen=True)
class AnnotationObject:
    """One validated object from a Pascal VOC annotation."""

    class_name: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass(frozen=True)
class InspectionResult:
    """Dataset inspection result suitable for reporting and tests."""

    report: pd.DataFrame
    classes: tuple[str, ...]
    image_paths: tuple[Path, ...]
    annotation_paths: tuple[Path, ...]


def _find_files() -> tuple[list[Path], list[Path]]:
    return sorted(IMAGE_ROOT.rglob("*.jpg")), sorted(ANNOTATION_ROOT.rglob("*.xml"))


def parse_voc_annotation(annotation_path: Path) -> tuple[tuple[int, int], list[AnnotationObject]]:
    """Parse one Pascal VOC XML annotation without modifying it."""

    root = ET.parse(annotation_path).getroot()
    size = root.find("size")
    if size is None:
        raise ValueError(f"Missing image size in annotation: {annotation_path.name}")
    width = int(float(size.findtext("width", "0")))
    height = int(float(size.findtext("height", "0")))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size in annotation: {annotation_path.name}")

    objects = []
    for element in root.findall("object"):
        name = (element.findtext("name") or "").strip().lower()
        box = element.find("bndbox")
        if not name or box is None:
            raise ValueError(f"Incomplete object in annotation: {annotation_path.name}")
        values = [float(box.findtext(key, "nan")) for key in ("xmin", "ymin", "xmax", "ymax")]
        object_record = AnnotationObject(name, *values)
        if (
            not all(pd.notna(value) for value in values)
            or object_record.xmin < 0
            or object_record.ymin < 0
            or object_record.xmax > width
            or object_record.ymax > height
            or object_record.xmin >= object_record.xmax
            or object_record.ymin >= object_record.ymax
        ):
            raise ValueError(f"Invalid bounding box in annotation: {annotation_path.name}")
        objects.append(object_record)
    return (width, height), objects


def _oriented_box(box: AnnotationObject, width: int, height: int, orientation: int) -> AnnotationObject:
    """Transform XML coordinates into the pixel orientation used for training."""

    if orientation == 6:
        return AnnotationObject(box.class_name, height - box.ymax, box.xmin, height - box.ymin, box.xmax)
    if orientation == 8:
        return AnnotationObject(box.class_name, box.ymin, width - box.xmax, box.ymax, width - box.xmin)
    if orientation == 3:
        return AnnotationObject(box.class_name, width - box.xmax, height - box.ymax, width - box.xmin, height - box.ymin)
    return box


def inspect_dataset() -> InspectionResult:
    """Inspect images, XML annotations, pairing, dimensions, and classes."""

    image_paths, annotation_paths = _find_files()
    image_by_stem = {path.stem: path for path in image_paths}
    annotation_by_stem = {path.stem: path for path in annotation_paths}
    classes = Counter()
    dimensions = Counter()
    invalid_images = []
    invalid_annotations = []
    dimension_mismatches = 0
    orientation_mismatches = 0
    unresolved_dimension_mismatches = 0
    total_objects = 0

    for path in image_paths:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                dimensions[image.size] += 1
        except Exception as error:
            invalid_images.append(f"{path.name}: {error}")

    for path in annotation_paths:
        try:
            annotation_size, objects = parse_voc_annotation(path)
            total_objects += len(objects)
            classes.update(obj.class_name for obj in objects)
            image_path = image_by_stem.get(path.stem)
            if image_path is not None:
                with Image.open(image_path) as image:
                    if image.size != annotation_size:
                        dimension_mismatches += 1
                        if image.getexif().get(274, 1) in (3, 6, 8) and ImageOps.exif_transpose(image).size == annotation_size:
                            orientation_mismatches += 1
                        else:
                            unresolved_dimension_mismatches += 1
        except Exception as error:
            invalid_annotations.append(f"{path.name}: {error}")

    missing_images = sorted(set(annotation_by_stem) - set(image_by_stem))
    missing_annotations = sorted(set(image_by_stem) - set(annotation_by_stem))
    report = pd.DataFrame([{
        "dataset": str(DATASET_ROOT.relative_to(DATA_DIR)),
        "image_count": len(image_paths),
        "annotation_count": len(annotation_paths),
        "object_count": total_objects,
        "annotation_format": "Pascal VOC XML",
        "yolo_compatible": False,
        "classes": ";".join(sorted(classes)),
        "class_distribution": json.dumps(dict(sorted(classes.items()))),
        "image_dimensions": json.dumps({f"{w}x{h}": count for (w, h), count in sorted(dimensions.items())}),
        "corrupt_images": len(invalid_images),
        "invalid_annotations": len(invalid_annotations),
        "dimension_mismatches": dimension_mismatches,
        "orientation_mismatches": orientation_mismatches,
        "unresolved_dimension_mismatches": unresolved_dimension_mismatches,
        "images_without_annotations": len(missing_annotations),
        "annotations_without_images": len(missing_images),
        "train_images": 0,
        "validation_images": 0,
        "test_images": 0,
        "status": "PASS" if not invalid_images and not invalid_annotations and not missing_images and not missing_annotations and not unresolved_dimension_mismatches else "REVIEW",
        "notes": "Only fire is annotated; smoke is not present. EXIF orientation mismatches are corrected during conversion. No original files are modified.",
    }])
    return InspectionResult(report, tuple(sorted(classes)), tuple(image_paths), tuple(annotation_paths))


def write_dataset_report(output_path: Path = PROCESSED_DIR / "dl_dataset_report.csv") -> pd.DataFrame:
    """Inspect the dataset and write its quality report."""

    result = inspect_dataset()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.report.to_csv(output_path, index=False, encoding="utf-8-sig")
    return result.report


def prepare_yolo_dataset(
    output_root: Path = YOLO_OUTPUT_ROOT,
    train_fraction: float = 0.8,
    validation_fraction: float = 0.1,
) -> pd.DataFrame:
    """Convert Pascal VOC to YOLO labels and deterministic image splits."""

    result = inspect_dataset()
    if result.report.iloc[0]["status"] != "PASS":
        raise ValueError("DL dataset quality checks did not pass; conversion was not started")
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1 or train_fraction + validation_fraction >= 1:
        raise ValueError("Split fractions must be positive and leave a non-empty test split")

    class_names = list(result.classes)
    class_ids = {name: index for index, name in enumerate(class_names)}
    annotation_by_stem = {path.stem: path for path in result.annotation_paths}
    image_paths = list(result.image_paths)
    train_end = int(len(image_paths) * train_fraction)
    validation_end = train_end + int(len(image_paths) * validation_fraction)
    split_paths = {
        "train": image_paths[:train_end],
        "val": image_paths[train_end:validation_end],
        "test": image_paths[validation_end:],
    }

    for split, paths in split_paths.items():
        image_dir = output_root / "images" / split
        label_dir = output_root / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        for image_path in paths:
            with Image.open(image_path) as image:
                orientation = image.getexif().get(274, 1)
                oriented_image = ImageOps.exif_transpose(image).convert("RGB")
                oriented_image.save(image_dir / image_path.name, format="JPEG", quality=95)
            annotation_size, objects = parse_voc_annotation(annotation_by_stem[image_path.stem])
            width, height = annotation_size
            output_width, output_height = oriented_image.size
            labels = []
            for obj in objects:
                center_x = ((obj.xmin + obj.xmax) / 2) / output_width
                center_y = ((obj.ymin + obj.ymax) / 2) / output_height
                box_width = (obj.xmax - obj.xmin) / output_width
                box_height = (obj.ymax - obj.ymin) / output_height
                labels.append(f"{class_ids[obj.class_name]} {center_x:.6f} {center_y:.6f} {box_width:.6f} {box_height:.6f}")
            (label_dir / f"{image_path.stem}.txt").write_text("\n".join(labels), encoding="utf-8")

    yaml_text = (
        f"path: {output_root.resolve().as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        f"nc: {len(class_names)}\n"
        f"names: {json.dumps(class_names)}\n"
    )
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "dataset.yaml").write_text(yaml_text, encoding="utf-8")
    report = result.report.copy()
    report.loc[0, "yolo_compatible"] = True
    report.loc[0, "train_images"] = len(split_paths["train"])
    report.loc[0, "validation_images"] = len(split_paths["val"])
    report.loc[0, "test_images"] = len(split_paths["test"])
    report.loc[0, "annotation_format"] = "Pascal VOC XML converted to YOLO TXT"
    return report


if __name__ == "__main__":
    print(write_dataset_report().to_string(index=False))
    print(prepare_yolo_dataset().to_string(index=False))