"""Central project paths and environment-backed application settings."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
ML_MODEL_DIR = MODEL_DIR / "ml"
DL_MODEL_DIR = MODEL_DIR / "dl"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
INSPECTION_REPORT = DATA_DIR / "inspection" / "ncrb_table_inventory.csv"
QUALITY_REPORT = PROCESSED_DIR / "data_quality_report.csv"

SQLITE_PATH = PROJECT_ROOT / "database" / "crime_x.sqlite3"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_PATH.as_posix()}")
