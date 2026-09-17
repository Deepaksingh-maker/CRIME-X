"""ML dataset inspection and leakage-aware feature construction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import DATA_DIR, PROCESSED_DIR
from src.data.cleaner import clean_dataframe, normalize_column_name
from src.data.dataset_registry import inventory_path
from src.data.loader import load_csv


YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")
BEST_ML_DATASET = "NCRB_Table_10A.1.csv"


@dataclass(frozen=True)
class MLProblem:
    """The selected ML problem and its evidence-based constraints."""

    name: str
    dataset: str
    target: str
    task: str
    features: tuple[str, ...]
    suitability: str
    reason: str


SELECTED_PROBLEM = MLProblem(
    name="State-level offences-against-state count prediction",
    dataset=BEST_ML_DATASET,
    target="target_count",
    task="regression",
    features=("lag_2020_count", "lag_2021_count", "population_2022_lakhs"),
    suitability="LIMITED_CANDIDATE",
    reason=(
        "39 states have annual counts for 2020-2022. The 2022 count can be defined "
        "from prior-year counts and population, but only one future year is available "
        "per state, so this is suitable for feature-engineering demonstration only."
    ),
)


def _years_from_columns(columns: list[str]) -> list[int]:
    years = set()
    for column in columns:
        years.update(int(value) for value in YEAR_PATTERN.findall(str(column)))
    return sorted(years)


def _years_from_values(dataframe: pd.DataFrame) -> list[int]:
    year_columns = [column for column in dataframe.columns if normalize_column_name(column) == "year"]
    if not year_columns:
        return []
    values = pd.to_numeric(dataframe[year_columns[0]], errors="coerce").dropna()
    return sorted({int(value) for value in values if 1900 <= value <= 2100})


def _source_years(path: Path, dataframe: pd.DataFrame) -> list[int]:
    years = sorted(set(_years_from_columns([str(column) for column in dataframe.columns]) + _years_from_values(dataframe)))
    if not years and "2022" in str(path):
        years = [2022]
    return years


def _candidate_text(dataframe: pd.DataFrame, state_available: bool, district_available: bool) -> tuple[str, str]:
    columns = [normalize_column_name(column) for column in dataframe.columns]
    numeric = [column for column in columns if any(token in column for token in ("count", "cases", "incidence", "crime", "total"))]
    target_candidates = numeric[:8]
    features = [column for column in columns if column not in {"sl_no", "state_ut", "district", "year"}][:12]
    if state_available and len(_years_from_columns(columns)) >= 2:
        reason = "State-level annual count columns can be reshaped into chronological observations."
    elif district_available:
        reason = "District and crime-count fields exist, but the table is a 2022 snapshot without historical rows."
    elif len(_years_from_columns(columns)) >= 2:
        reason = "Multiple year columns exist, but no compatible state/district key is available."
    else:
        reason = "No compatible state/district historical structure was found."
    return ";".join(target_candidates), ";".join(features)


def inspect_ml_datasets() -> pd.DataFrame:
    """Inspect every NCRB/cybercrime CSV and assess ML suitability."""

    inventory = pd.read_csv(inventory_path(), low_memory=False)
    inventory_rows = inventory.set_index("file_name")["rows"].to_dict()
    paths = sorted(list((DATA_DIR / "ncrb 2022" / "data").glob("*.csv")) + list((DATA_DIR / "cyber crime").glob("*.csv")))
    reports = []
    for path in paths:
        dataframe = load_csv(path)
        cleaned = clean_dataframe(dataframe)
        columns = [str(column) for column in cleaned.columns]
        normalized = [normalize_column_name(column) for column in columns]
        state_available = any("state" in column for column in normalized)
        district_available = any("district" in column for column in normalized)
        years = _source_years(path, dataframe)
        target_candidates, feature_candidates = _candidate_text(dataframe, state_available, district_available)
        if path.name == BEST_ML_DATASET:
            suitability = SELECTED_PROBLEM.suitability
            reason = SELECTED_PROBLEM.reason
            target_candidates = "offences_against_state_count_2020;offences_against_state_count_2021;offences_against_state_count_2022"
            feature_candidates = ";".join(SELECTED_PROBLEM.features)
        elif district_available and years == [2022]:
            suitability = "NOT_SUITABLE"
            reason = "2022-only district snapshot; cannot support temporal prediction without future or prior years."
        elif len(years) >= 2 and state_available:
            suitability = "SECONDARY_CANDIDATE"
            reason = "State-level multi-year counts exist, but target semantics and available history require further review."
        elif len(years) >= 2:
            suitability = "NOT_SUITABLE"
            reason = "Multi-year columns exist, but there is no compatible state/district panel key."
        else:
            suitability = "NOT_SUITABLE"
            reason = "Insufficient historical years for a defensible temporal ML task."
        reports.append({
            "dataset": str(path.relative_to(DATA_DIR)),
            "years_available": ";".join(map(str, years)),
            "number_of_rows": int(inventory_rows.get(path.name, len(dataframe))),
            "state_available": state_available,
            "district_available": district_available,
            "target_candidates": target_candidates,
            "feature_candidates": feature_candidates,
            "ML_suitability": suitability,
            "reason": reason,
        })
    return pd.DataFrame(reports).sort_values("dataset").reset_index(drop=True)


def write_ml_dataset_report(output_path: Path = PROCESSED_DIR / "ml_dataset_report.csv") -> pd.DataFrame:
    """Write the actual-dataset ML suitability report."""

    report = inspect_ml_datasets()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False, encoding="utf-8-sig")
    return report


def build_selected_state_features(path: Path | None = None) -> pd.DataFrame:
    """Build leakage-aware 2022 state features from the selected wide table."""

    source = path or DATA_DIR / "ncrb 2022" / "data" / BEST_ML_DATASET
    dataframe = clean_dataframe(load_csv(source))
    required = {"state_ut", "2020", "2021", "2022", "mid_year_projected_population_in_lakhs"}
    missing = sorted(required - set(dataframe.columns))
    if missing:
        raise ValueError(f"Selected ML dataset is missing columns: {', '.join(missing)}")
    result = dataframe[[
        "state_ut", "2020", "2021", "2022", "mid_year_projected_population_in_lakhs"
    ]].rename(columns={
        "2020": "lag_2020_count",
        "2021": "lag_2021_count",
        "2022": "target_count",
        "mid_year_projected_population_in_lakhs": "population_2022_lakhs",
    })
    result = result[result["state_ut"].astype("string").str.lower() != "total states"].copy()
    return result.reset_index(drop=True)