from pathlib import Path

from src.dl.dataset_inspection import (
    prepare_yolo_dataset,
    inspect_dataset,
    write_dataset_report,
)
from src.dl.preprocess import validate_image_bytes


def test_real_dataset_inspection():
    result = inspect_dataset()
    report = result.report.iloc[0]
    assert report["image_count"] == 100
    assert report["annotation_count"] == 100
    assert report["object_count"] == 122
    assert result.classes == ("fire",)
    assert report["annotation_format"] == "Pascal VOC XML"
    assert report["corrupt_images"] == 0
    assert report["images_without_annotations"] == 0


def test_yolo_conversion_creates_deterministic_splits_without_fake_classes(tmp_path: Path):
    report = prepare_yolo_dataset(tmp_path / "dl_yolo")
    row = report.iloc[0]
    assert bool(row["yolo_compatible"])
    assert row["train_images"] == 80
    assert row["validation_images"] == 10
    assert row["test_images"] == 10
    assert (tmp_path / "dl_yolo" / "dataset.yaml").is_file()
    assert len(list((tmp_path / "dl_yolo" / "labels" / "train").glob("*.txt"))) == 80
    assert "smoke" not in row["classes"]


def test_report_is_written(tmp_path: Path):
    output = tmp_path / "dl_dataset_report.csv"
    report = write_dataset_report(output)
    assert output.is_file()
    assert report.iloc[0]["status"] == "PASS"


def test_uploaded_image_validation():
    image = validate_image_bytes(Path("data/deep learning/India Fire & Smoke Dataset/Datacluster Fire and Smoke Sample/Datacluster Fire and Smoke Sample/Datacluster Fire and Smoke Sample (1).jpg").read_bytes(), "image.jpg")
    assert image.mode == "RGB"