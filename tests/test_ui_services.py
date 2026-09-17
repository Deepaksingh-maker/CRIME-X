from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, CrimeRecord
from src.database.repository import Repository
from src.database.seed import seed_processed_data
from src.services.ai_service import ask_crime_x
from src.services.tts_service import text_to_speech


def test_sqlite_dashboard_backend_has_real_records():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    counts = seed_processed_data(Repository(session))
    assert counts["physical_crime"] == 934
    assert session.query(CrimeRecord).count() == 939


def test_assistant_and_tts_are_explicit_placeholders():
    answer = ask_crime_x("What is the top district?")
    audio = text_to_speech("No answer")
    assert answer["status"] == "ok"
    assert "District" in answer["answer"]
    assert audio["audio"] is None


def test_dashboard_image_asset_exists():
    assert next(Path("data/processed/dl_yolo/images/test").glob("*.jpg")).is_file()