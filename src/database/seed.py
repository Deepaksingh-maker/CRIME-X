"""Idempotent import of processed CRIME X datasets into SQLAlchemy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import PROCESSED_DIR
from src.data.analysis import CYBER_CATEGORY_COLUMNS, FRAUD_CATEGORY_COLUMNS, PHYSICAL_TOTAL_COLUMN
from src.data.cleaner import clean_dataframe
from src.data.loader import load_csv

from .repository import Repository


def _records_from_physical(path: Path) -> list[dict]:
    dataframe = clean_dataframe(load_csv(path))
    dataframe = dataframe[~dataframe["state_ut"].astype("string").str.lower().str.contains("total|grand total", na=False)]
    records = []
    for row in dataframe.to_dict(orient="records"):
        records.append({
            "state": row["state_ut"],
            "district": row["district"],
            "year": 2022,
            "crime_type": "total_cognizable_ipc_crimes",
            "crime_count": row[PHYSICAL_TOTAL_COLUMN],
            "source_dataset": "NCRB_District_Table_1.1.csv",
            "source_year": 2022,
            "granularity": "district",
        })
    return records


def _records_from_cyber(path: Path) -> list[dict]:
    dataframe = clean_dataframe(load_csv(path))
    dataframe = dataframe[~dataframe["state_ut"].astype("string").str.lower().str.contains("total|grand total", na=False)]
    category_columns = {**CYBER_CATEGORY_COLUMNS, **FRAUD_CATEGORY_COLUMNS, "total_cyber_crimes": "total_cyber_crimes_a_b_c_col_51"}
    records = []
    for row in dataframe.to_dict(orient="records"):
        for category, column in category_columns.items():
            records.append({
                "state": row["state_ut"],
                "district": row["district"],
                "year": 2022,
                "crime_type": category,
                "crime_count": row.get(column, 0) or 0,
                "source_dataset": "NCRB_District_Table_1.9.csv",
                "source_year": 2022,
                "metrics": {"granularity": "district", "category_source_column": column},
            })
    return records


def _records_from_gujarat(path: Path) -> list[dict]:
    dataframe = clean_dataframe(load_csv(path))
    return [{
        "state": "Gujarat",
        "district": None,
        "year": int(row["year"]),
        "crime_type": "total_crimes_recorded",
        "crime_count": row["total_number_of_crimes_recorded"],
        "source_dataset": "D47-Crimes_16_1.csv",
        "source_year": int(row["year"]),
        "granularity": "city",
        "metrics": {"city": row["city_name"]},
    } for row in dataframe.to_dict(orient="records")]


def seed_processed_data(repository: Repository, processed_dir: Path = PROCESSED_DIR) -> dict[str, int]:
    """Insert processed physical, cybercrime, and Gujarat records idempotently."""

    physical = repository.insert_crime_records(_records_from_physical(processed_dir / "physical_crime_2022_clean.csv"))
    gujarat = repository.insert_crime_records(_records_from_gujarat(processed_dir / "gujarat_crime_clean.csv"))
    cyber = repository.insert_cybercrime_records(_records_from_cyber(processed_dir / "cybercrime_2022_clean.csv"))
    return {"physical_crime": physical, "gujarat": gujarat, "cybercrime": cyber}