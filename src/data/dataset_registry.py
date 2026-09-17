"""Approved real datasets and their intended analytical boundaries."""

from dataclasses import dataclass
from pathlib import Path
from config import INSPECTION_REPORT, PROJECT_ROOT


@dataclass(frozen=True)
class DatasetSpec:
    """Metadata for a dataset approved for a project module."""

    name: str
    path: Path
    purpose: str
    granularity: str
    year_coverage: str
    required_columns: tuple[str, ...] = ()
    notes: str = ""


DATASETS = {
    "physical_crime": DatasetSpec(
        name="NCRB district physical crime table 1.1",
        path=PROJECT_ROOT / "data" / "ncrb 2022" / "data" / "NCRB_District_Table_1.1.csv",
        purpose="District-level physical crime analytics",
        granularity="State/UT and district, 2022",
        year_coverage="2022",
        required_columns=("State/UT", "District"),
        notes="Use as a 2022 district snapshot; do not combine with time-series tables without compatible keys.",
    ),
    "cybercrime": DatasetSpec(
        name="NCRB district cybercrime table 1.9",
        path=PROJECT_ROOT / "data" / "cyber crime" / "NCRB_District_Table_1.9.csv",
        purpose="District and category-level cybercrime analytics",
        granularity="State/UT and district, 2022",
        year_coverage="2022",
        required_columns=("State/UT", "District"),
        notes="Historical aggregate data; it does not support claims of real-time detection.",
    ),
    "gujarat": DatasetSpec(
        name="Ahmedabad historical crime series",
        path=PROJECT_ROOT / "data" / "gujarat" / "D47-Crimes_16_1.csv",
        purpose="Gujarat/Ahmedabad historical trend analysis",
        granularity="City and year",
        year_coverage="2014-2018",
        required_columns=("City Name", "Year", "Total number of crimes recorded"),
        notes="Keep separate from the 2022 district-level NCRB datasets.",
    ),
    "ml_candidate": DatasetSpec(
        name="Ahmedabad historical crime series",
        path=PROJECT_ROOT / "data" / "gujarat" / "D47-Crimes_16_1.csv",
        purpose="Candidate for exploratory chronological trend modelling",
        granularity="City and year",
        year_coverage="2014-2018",
        required_columns=("City Name", "Year", "Total number of crimes recorded"),
        notes="Only five observations; suitability must be evaluated before training or presenting a model.",
    ),
    "deep_learning": DatasetSpec(
        name="India Fire & Smoke Dataset",
        path=PROJECT_ROOT / "data" / "deep learning" / "India Fire & Smoke Dataset",
        purpose="Fire and smoke safety image detection",
        granularity="Images with annotations",
        year_coverage="Not specified",
        notes="Safety intelligence feature, not crime detection. Image and annotation counts must be checked before training.",
    ),
    "folium_analytics": DatasetSpec(
        name="NCRB district physical crime table 1.1",
        path=PROJECT_ROOT / "data" / "ncrb 2022" / "data" / "NCRB_District_Table_1.1.csv",
        purpose="Analytical input for a future map",
        granularity="State/UT and district, 2022",
        year_coverage="2022",
        required_columns=("State/UT", "District"),
        notes="No coordinates are assumed. A verified boundary/centroid dataset is required before mapping.",
    ),
}


def get_dataset(name: str) -> DatasetSpec:
    """Return an approved dataset specification by module name."""

    try:
        return DATASETS[name]
    except KeyError as error:
        available = ", ".join(sorted(DATASETS))
        raise KeyError(f"Unknown dataset '{name}'. Available: {available}") from error


def inventory_path() -> Path:
    """Return the generated NCRB inventory path."""

    return INSPECTION_REPORT