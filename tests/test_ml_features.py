from pathlib import Path

import pandas as pd

from src.ml.features import (
    BEST_ML_DATASET,
    build_selected_state_features,
    inspect_ml_datasets,
    write_ml_dataset_report,
)
from src.ml.preprocess import chronological_split, prepare_regression_data


def test_ml_report_contains_selected_real_dataset():
    report = inspect_ml_datasets()
    selected = report[report["dataset"].str.endswith(BEST_ML_DATASET)]
    assert len(selected) == 1
    assert selected.iloc[0]["years_available"] == "2020;2021;2022"
    assert selected.iloc[0]["ML_suitability"] == "LIMITED_CANDIDATE"


def test_selected_features_have_real_state_rows_and_no_leakage_rates():
    features = build_selected_state_features()
    assert len(features) == 39
    assert set(features.columns) == {
        "state_ut", "lag_2020_count", "lag_2021_count", "target_count", "population_2022_lakhs"
    }
    assert not any("rate" in column for column in features.columns)


def test_preprocessing_and_chronological_split():
    features = build_selected_state_features()
    x_data, target = prepare_regression_data(features)
    train, test = chronological_split(features)
    assert x_data.shape == (39, 3)
    assert len(target) == 39
    assert len(train) + len(test) == 39
    assert train.index.max() < test.index.min()


def test_ml_report_is_written(tmp_path: Path):
    output = tmp_path / "ml_dataset_report.csv"
    report = write_ml_dataset_report(output)
    assert output.is_file()
    assert len(pd.read_csv(output)) == len(report)