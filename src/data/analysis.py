"""Real-data exploratory analysis functions for CRIME X."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .cleaner import clean_dataframe
from .dataset_registry import get_dataset
from .loader import load_csv


IDENTIFIER_COLUMNS = {"sl_no", "state_ut", "district", "city_name", "year"}
PHYSICAL_TOTAL_COLUMN = "total_cognizable_ipc_crimes_col_144"
CYBER_TOTAL_COLUMN = "total_cyber_crimes_a_b_c_col_51"

CYBER_CATEGORY_COLUMNS = {
    "Ransomware": "a_offences_under_i_t_act_computer_related_offences_computer_related_offences_sec_66_ransom_ware_col_6",
    "Identity theft": "a_offences_under_i_t_act_computer_related_offences_identity_theft_sec_66c_col_9",
    "Cyber terrorism": "a_offences_under_i_t_act_cyber_terrorism_sec_66_f_col_12",
    "Fake profile": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fake_profile_r_w_ipc_sll_col_37",
    "Cyber blackmailing/threatening": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_cyber_blackmailing_threatening_sec_506_503_384_ipc_r_w_ipc_sll_col_41",
    "Fake news/social media": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fake_news_on_social_media_sec_505_col_42",
}

FRAUD_CATEGORY_COLUMNS = {
    "Credit/debit card fraud": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fraud_sec_420_r_w_sec_465_468_471_ipc_credit_card_debit_card_col_29",
    "ATM fraud": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fraud_sec_420_r_w_sec_465_468_471_ipc_atms_col_30",
    "Online banking fraud": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fraud_sec_420_r_w_sec_465_468_471_ipc_online_banking_fraud_col_31",
    "OTP fraud": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fraud_sec_420_r_w_sec_465_468_471_ipc_otp_frauds_col_32",
    "Other fraud": "b_offences_under_ipc_involving_communication_devices_as_medium_target_r_w_it_act_fraud_sec_420_r_w_sec_465_468_471_ipc_others_col_33",
}


def load_analysis_dataset(dataset_name: str, processed: bool = True) -> pd.DataFrame:
    """Load and clean a registered dataset without changing its source file."""

    spec = get_dataset(dataset_name)
    path = spec.path
    if processed and dataset_name in {"cybercrime", "gujarat"}:
        filename = "cybercrime_2022_clean.csv" if dataset_name == "cybercrime" else "gujarat_crime_clean.csv"
        path = path.parents[1] / "processed" / filename
    return _exclude_aggregate_rows(clean_dataframe(load_csv(path)))


def _validate_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Required analysis columns are missing: {', '.join(missing)}")


def _exclude_aggregate_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove NCRB summary rows before district/state aggregation."""

    filtered = dataframe.copy()
    for column in ("state_ut", "district"):
        if column in filtered.columns:
            values = filtered[column].astype("string").str.lower()
            filtered = filtered[~values.str.contains("total|grand total|all india", na=False)]
    return filtered.reset_index(drop=True)


def _rank_by_column(dataframe: pd.DataFrame, group_column: str, value_column: str, limit: int) -> pd.DataFrame:
    _validate_columns(dataframe, (group_column, value_column))
    result = (
        dataframe.groupby(group_column, dropna=False, as_index=False)[value_column]
        .sum()
        .rename(columns={value_column: "total_cases"})
        .sort_values("total_cases", ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )
    return result


def state_ranking(dataframe: pd.DataFrame, value_column: str, limit: int = 10) -> pd.DataFrame:
    """Rank states by a real numeric crime measure."""

    return _rank_by_column(dataframe, "state_ut", value_column, limit)


def district_ranking(dataframe: pd.DataFrame, value_column: str, limit: int = 10) -> pd.DataFrame:
    """Rank districts by a real numeric crime measure."""

    return _rank_by_column(dataframe, "district", value_column, limit)


def category_distribution(dataframe: pd.DataFrame, category_columns: dict[str, str]) -> pd.DataFrame:
    """Aggregate explicitly selected categories, avoiding nested total double-counting."""

    available = {label: column for label, column in category_columns.items() if column in dataframe.columns}
    if not available:
        raise ValueError("None of the requested category columns exist in the dataset")
    return pd.DataFrame(
        [{"category": label, "total_cases": float(dataframe[column].sum())} for label, column in available.items()]
    ).sort_values("total_cases", ascending=False).reset_index(drop=True)


def year_wise_analysis(dataframe: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Aggregate a real time-series dataset by year."""

    _validate_columns(dataframe, ("year", value_column))
    return (
        dataframe.groupby("year", as_index=False)[value_column]
        .sum()
        .rename(columns={value_column: "total_cases"})
        .sort_values("year")
        .reset_index(drop=True)
    )


def gujarat_analysis(dataframe: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Analyze the separate Ahmedabad 2014-2018 historical series."""

    dataframe = dataframe if dataframe is not None else load_analysis_dataset("gujarat")
    dataframe = _exclude_aggregate_rows(clean_dataframe(dataframe))
    yearly = year_wise_analysis(dataframe, "total_number_of_crimes_recorded")
    yearly["year_over_year_change"] = yearly["total_cases"].pct_change() * 100
    return {"yearly": yearly, "source": dataframe}


def cybercrime_analysis(dataframe: pd.DataFrame | None = None) -> dict[str, object]:
    """Return district, state, category, and fraud analysis for NCRB cybercrime data."""

    dataframe = dataframe if dataframe is not None else load_analysis_dataset("cybercrime")
    dataframe = _exclude_aggregate_rows(clean_dataframe(dataframe))
    _validate_columns(dataframe, ("state_ut", "district", CYBER_TOTAL_COLUMN))
    return {
        "total_cyber_crimes": float(dataframe[CYBER_TOTAL_COLUMN].sum()),
        "state_ranking": state_ranking(dataframe, CYBER_TOTAL_COLUMN),
        "district_ranking": district_ranking(dataframe, CYBER_TOTAL_COLUMN),
        "category_distribution": category_distribution(dataframe, CYBER_CATEGORY_COLUMNS),
        "fraud_distribution": category_distribution(dataframe, FRAUD_CATEGORY_COLUMNS),
        "source": dataframe,
    }


def physical_crime_analysis(dataframe: pd.DataFrame | None = None) -> dict[str, object]:
    """Analyze the 2022 district physical-crime snapshot."""

    dataframe = dataframe if dataframe is not None else load_analysis_dataset("physical_crime", processed=False)
    dataframe = _exclude_aggregate_rows(clean_dataframe(dataframe))
    _validate_columns(dataframe, ("state_ut", "district", PHYSICAL_TOTAL_COLUMN))
    return {
        "total_crime": float(dataframe[PHYSICAL_TOTAL_COLUMN].sum()),
        "state_ranking": state_ranking(dataframe, PHYSICAL_TOTAL_COLUMN),
        "district_ranking": district_ranking(dataframe, PHYSICAL_TOTAL_COLUMN),
        "source": dataframe,
        "is_time_series": False,
    }