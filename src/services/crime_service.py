"""Service API for physical-crime analytics."""

from __future__ import annotations

import pandas as pd

from src.data.analysis import PHYSICAL_TOTAL_COLUMN, district_ranking, load_analysis_dataset, physical_crime_analysis, state_ranking
from src.database.repository import Repository

from ._serialization import to_jsonable


def get_crime_overview(repository: Repository | None = None) -> dict[str, object]:
    """Return the real 2022 physical-crime overview without raw DataFrames."""

    if repository is None:
        return to_jsonable(physical_crime_analysis())
    records = repository.get_crime_records(crime_type="total_cognizable_ipc_crimes")
    dataframe = pd.DataFrame(records)
    total = float(dataframe["crime_count"].sum()) if not dataframe.empty else 0.0
    return {"total_crime": total, "record_count": len(records), "source": "sqlite"}


def get_state_ranking(limit: int = 10, repository: Repository | None = None) -> list[dict[str, object]]:
    """Return state rankings for total cognizable IPC crime."""

    if repository is None:
        dataframe = load_analysis_dataset("physical_crime", processed=False)
        return to_jsonable(state_ranking(dataframe, PHYSICAL_TOTAL_COLUMN, limit))
    records = repository.get_crime_records(crime_type="total_cognizable_ipc_crimes")
    if not records:
        dataframe = load_analysis_dataset("physical_crime", processed=False)
        return to_jsonable(state_ranking(dataframe, PHYSICAL_TOTAL_COLUMN, limit))
    dataframe = pd.DataFrame(records)
    return to_jsonable(state_ranking(dataframe.rename(columns={"state": "state_ut", "crime_count": "crime_value"}), "crime_value", limit))


def get_district_ranking(limit: int = 10, repository: Repository | None = None) -> list[dict[str, object]]:
    """Return district rankings for total cognizable IPC crime."""

    if repository is None:
        dataframe = load_analysis_dataset("physical_crime", processed=False)
        return to_jsonable(district_ranking(dataframe, PHYSICAL_TOTAL_COLUMN, limit))
    records = repository.get_crime_records(crime_type="total_cognizable_ipc_crimes")
    if not records:
        dataframe = load_analysis_dataset("physical_crime", processed=False)
        return to_jsonable(district_ranking(dataframe, PHYSICAL_TOTAL_COLUMN, limit))
    dataframe = pd.DataFrame(records)
    return to_jsonable(district_ranking(dataframe.rename(columns={"crime_count": "crime_value"}), "crime_value", limit))