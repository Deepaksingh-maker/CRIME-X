from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.database.repository import Repository
from src.database.seed import seed_processed_data
from src.database.schema import create_schema


def repository():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Repository(sessionmaker(bind=engine, expire_on_commit=False)())


def test_crime_insert_retrieve_and_duplicate_protection():
    repo = repository()
    record = {"state": "Gujarat", "district": "Ahmedabad", "year": 2022, "crime_type": "test_total", "crime_count": 10, "source_dataset": "test.csv", "source_year": 2022, "granularity": "district"}
    assert repo.insert_crime_records([record]) == 1
    assert repo.insert_crime_records([record]) == 0
    assert len(repo.get_state_crime("Gujarat")) == 1
    assert len(repo.get_district_crime("Ahmedabad")) == 1


def test_cyber_prediction_and_fire_storage():
    repo = repository()
    cyber = {"state": "Gujarat", "district": "Ahmedabad", "year": 2022, "crime_type": "Online banking fraud", "crime_count": 4, "source_dataset": "cyber.csv", "source_year": 2022}
    assert repo.insert_cybercrime_records([cyber]) == 1
    assert len(repo.get_cybercrime_records()) == 1
    assert len(repo.get_fraud_records()) == 1
    prediction = repo.save_prediction({"predicted_count": 4, "model": "test", "confidence": None, "warning": "limited", "input_features": {"x": 1}})
    assert len(repo.get_prediction_history()) == 1
    detection = repo.save_fire_detection({"image_path": "test.jpg", "detections": [], "image_width": 10, "image_height": 20})
    assert detection["image_width"] == 10
    assert len(repo.get_fire_detection_history()) == 1


def test_investigation_and_alert_crud():
    repo = repository()
    created = repo.create_investigation({"case_reference": "CASE-1", "title": "Test case"})
    assert created["status"] == "OPEN"
    updated = repo.update_investigation("CASE-1", {"status": "CLOSED"})
    assert updated["status"] == "CLOSED"
    alert = repo.create_alert({"alert_type": "TEST", "severity": "INFO", "message": "hello"})
    assert len(repo.get_alerts(unread_only=True)) == 1
    repo.mark_alert_read(alert["id"])
    assert repo.get_alerts(unread_only=True) == []


def test_processed_seed_is_idempotent():
    repo = repository()
    first = seed_processed_data(repo)
    second = seed_processed_data(repo)
    assert first["physical_crime"] == 934
    assert first["gujarat"] == 5
    assert first["cybercrime"] > 0
    assert second == {"physical_crime": 0, "gujarat": 0, "cybercrime": 0}