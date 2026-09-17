"""Reproducible processing entry points for approved tabular datasets."""

from pathlib import Path

from config import PROCESSED_DIR, QUALITY_REPORT

from .cleaner import clean_dataframe
from .dataset_registry import DATASETS, DatasetSpec
from .loader import load_csv
from .validator import build_quality_report


OUTPUT_NAMES = {
    "physical_crime": "physical_crime_2022_clean.csv",
    "cybercrime": "cybercrime_2022_clean.csv",
    "gujarat": "gujarat_crime_clean.csv",
}


def process_csv_dataset(spec: DatasetSpec, output_path: Path) -> Path:
    """Clean one approved CSV and write it beneath the processed-data directory."""

    cleaned = clean_dataframe(load_csv(spec.path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def process_phase_one(output_dir: Path = PROCESSED_DIR) -> dict[str, Path]:
    """Generate approved processed datasets and the quality report."""

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        key: process_csv_dataset(DATASETS[key], output_dir / filename)
        for key, filename in OUTPUT_NAMES.items()
    }
    build_quality_report(DATASETS.values(), output_dir / QUALITY_REPORT.name)
    outputs["quality_report"] = output_dir / QUALITY_REPORT.name
    return outputs


if __name__ == "__main__":
    for name, path in process_phase_one().items():
        print(f"{name}: {path}")