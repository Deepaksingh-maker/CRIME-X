from pathlib import Path
from typing import Union

import pandas as pd

from config import DATA_DIR, PROCESSED_DIR, PROJECT_ROOT
from .dataset_registry import get_dataset


PathLike = Union[str, Path]


def load_csv(file_path: PathLike, **read_csv_kwargs) -> pd.DataFrame:
    """Load a CSV using UTF-8 first and common Indian-data fallbacks."""

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        return pd.read_csv(
            path,
            encoding="utf-8",
            low_memory=False,
            **read_csv_kwargs,
        )

    except UnicodeDecodeError:
        return pd.read_csv(
            path,
            encoding="cp1252",
            low_memory=False,
            **read_csv_kwargs,
        )


def load_ncrb_table(table_name: str) -> pd.DataFrame:
    """Load an approved NCRB table by registry key."""

    return load_csv(get_dataset(table_name).path)


def load_cybercrime_data() -> pd.DataFrame:
    """Load the approved district-level NCRB cybercrime table."""

    return load_ncrb_table("cybercrime")


def load_gujarat_crime_data() -> pd.DataFrame:
    """Load the separate Ahmedabad historical crime series."""

    return load_csv(get_dataset("gujarat").path)