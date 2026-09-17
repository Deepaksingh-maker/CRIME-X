from pathlib import Path

import pandas as pd

from src.data.cleaner import clean_dataframe, normalize_column_name
from src.data.dataset_registry import DATASETS, get_dataset
from src.data.loader import load_csv
from src.data.validator import validate_dataframe


def test_registry_paths_exist_for_csv_sources():
    for spec in DATASETS.values():
        if spec.path.suffix.lower() == ".csv":
            assert spec.path.is_file()


def test_loader_reads_registered_cybercrime_data():
    dataframe = load_csv(get_dataset("cybercrime").path)
    assert dataframe.shape == (970, 52)


def test_cleaner_preserves_zero_and_normalizes_columns():
    dataframe = pd.DataFrame({" State/UT ": [" Gujarat "], "Value": [0]})
    cleaned = clean_dataframe(dataframe)
    assert normalize_column_name(" State/UT ") in cleaned.columns
    assert cleaned.iloc[0]["value"] == 0


def test_validator_reports_required_columns_and_duplicates():
    dataframe = pd.DataFrame({"State/UT": ["Gujarat", "Gujarat"], "Year": [2022, 2022]})
    report = validate_dataframe(dataframe, ("State/UT", "Year"))
    assert report.iloc[0]["duplicate_rows"] == 1
    assert report.iloc[0]["missing_required_columns"] == ""
