"""Service API for cybercrime and fraud analytics."""

from __future__ import annotations

import pandas as pd

from src.data.analysis import cybercrime_analysis
from src.database.repository import Repository

from ._serialization import to_jsonable


def _analysis() -> dict[str, object]:
    return cybercrime_analysis()


def get_cybercrime_overview(repository: Repository | None = None) -> dict[str, object]:
    """Return cybercrime total and geographic rankings."""

    if repository is not None:
        records = repository.get_cybercrime_records(crime_type="total_cyber_crimes")
        return {"total_cyber_crimes": float(sum(record["crime_count"] for record in records)), "record_count": len(records), "source": "sqlite"}
    result = _analysis()
    return to_jsonable({
        "total_cyber_crimes": result["total_cyber_crimes"],
        "state_ranking": result["state_ranking"],
        "district_ranking": result["district_ranking"],
    })


def get_cybercrime_categories(repository: Repository | None = None) -> list[dict[str, object]]:
    """Return real cybercrime category totals."""

    if repository is not None:
        records = pd.DataFrame(repository.get_cybercrime_records())
        if records.empty:
            return []
        return to_jsonable(records.groupby("crime_type", as_index=False)["crime_count"].sum().rename(columns={"crime_type": "category", "crime_count": "total_cases"}).sort_values("total_cases", ascending=False))
    return to_jsonable(_analysis()["category_distribution"])


def get_fraud_analysis(repository: Repository | None = None) -> list[dict[str, object]]:
    """Return real cyber-fraud category totals."""

    if repository is not None:
        records = pd.DataFrame(repository.get_fraud_records())
        if records.empty:
            return []
        return to_jsonable(records.groupby("crime_type", as_index=False)["crime_count"].sum().rename(columns={"crime_type": "category", "crime_count": "total_cases"}).sort_values("total_cases", ascending=False))
    return to_jsonable(_analysis()["fraud_distribution"])