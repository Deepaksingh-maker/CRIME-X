"""Service facade for CRIME X exploratory analytics."""

from src.data.analysis import (
    cybercrime_analysis,
    district_ranking,
    gujarat_analysis,
    load_analysis_dataset,
    physical_crime_analysis,
    state_ranking,
    year_wise_analysis,
)


def get_crime_overview() -> dict[str, object]:
    """Return real physical-crime snapshot metrics."""

    return physical_crime_analysis()


def get_state_ranking(dataset_name: str, value_column: str, limit: int = 10):
    """Return a state ranking for a registered tabular dataset."""

    return state_ranking(load_analysis_dataset(dataset_name), value_column, limit)


def get_district_ranking(dataset_name: str, value_column: str, limit: int = 10):
    """Return a district ranking for a registered tabular dataset."""

    return district_ranking(load_analysis_dataset(dataset_name), value_column, limit)


def get_gujarat_analysis() -> dict[str, object]:
    """Return Ahmedabad's historical yearly analysis."""

    return gujarat_analysis()


def get_cybercrime_analysis() -> dict[str, object]:
    """Return NCRB cybercrime rankings and category analysis."""

    return cybercrime_analysis()


def get_year_analysis(dataset_name: str, value_column: str):
    """Return chronological aggregation when the source contains a year field."""

    return year_wise_analysis(load_analysis_dataset(dataset_name), value_column)