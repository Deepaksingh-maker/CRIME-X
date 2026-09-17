"""Dataset quality checks and report generation."""

from pathlib import Path
from typing import Iterable

import pandas as pd

from .cleaner import clean_dataframe, normalize_column_name
from .dataset_registry import DatasetSpec
from .loader import load_csv


def validate_dataframe(
    dataframe: pd.DataFrame,
    required_columns: Iterable[str] = (),
    dataset_name: str = "dataset",
) -> pd.DataFrame:
    """Create one-row quality metrics for a dataframe."""

    cleaned = clean_dataframe(dataframe)
    normalized_required = {normalize_column_name(column) for column in required_columns}
    missing_required = sorted(normalized_required - set(cleaned.columns))
    numeric_columns = cleaned.select_dtypes(include="number").columns
    negative_values = int((cleaned[numeric_columns] < 0).sum().sum()) if len(numeric_columns) else 0
    year_columns = [column for column in cleaned.columns if "year" in column]
    invalid_years = 0
    if year_columns:
        years = cleaned[year_columns[0]].dropna()
        invalid_years = int((~years.between(1900, 2100)).sum())

    return pd.DataFrame([{
        "dataset": dataset_name,
        "rows": len(cleaned),
        "columns": len(cleaned.columns),
        "duplicate_rows": int(cleaned.duplicated().sum()),
        "missing_cells": int(cleaned.isna().sum().sum()),
        "missing_required_columns": ";".join(missing_required),
        "negative_numeric_values": negative_values,
        "invalid_year_values": invalid_years,
        "status": "PASS" if not missing_required and not negative_values and not invalid_years else "REVIEW",
    }])


def validate_dataset(spec: DatasetSpec) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate a registered CSV dataset."""

    dataframe = load_csv(spec.path)
    return dataframe, validate_dataframe(dataframe, spec.required_columns, spec.name)


def build_quality_report(specs: Iterable[DatasetSpec], output_path: Path) -> pd.DataFrame:
    """Validate registered file datasets and write a CSV report."""

    reports = []
    for spec in specs:
        if spec.path.is_file() and spec.path.suffix.lower() == ".csv":
            _, report = validate_dataset(spec)
            reports.append(report)
        else:
            reports.append(pd.DataFrame([{
                "dataset": spec.name,
                "rows": pd.NA,
                "columns": pd.NA,
                "duplicate_rows": pd.NA,
                "missing_cells": pd.NA,
                "missing_required_columns": "",
                "negative_numeric_values": pd.NA,
                "invalid_year_values": pd.NA,
                "status": "NOT_CSV" if spec.path.is_dir() else "MISSING",
            }]))
    result = pd.concat(reports, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8-sig")
    return result