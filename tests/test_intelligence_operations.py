from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.database.repository import Repository
from src.services.ai_service import ask_crime_x, detect_intent


def repo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Repository(sessionmaker(bind=engine, expire_on_commit=False)())


def test_ai_routes_english_and_hinglish_queries():
    assert detect_intent("Which state has the highest crime?") == "state_ranking"
    assert detect_intent("India me sabse zyada crime kis state me hai?") == "state_ranking"
    assert detect_intent("Cyber fraud kaunsa highest hai?") == "fraud_analysis"


def test_ai_returns_real_service_response():
    result = ask_crime_x("Top 5 states by crime")
    assert result["status"] == "ok"
    assert "Uttar Pradesh" in result["answer"]
    assert "NCRB" in result["source"]


def test_ai_unknown_does_not_fabricate():
    result = ask_crime_x("Tell me a fictional crime statistic")
    assert result["status"] == "unavailable"
    assert "not available" in result["answer"]


def test_investigation_timeline_evidence_and_alert_lifecycle():
    repository = repo()
    repository.create_investigation({"case_reference": "CASE-OPS-1", "title": "Operations case", "case_type": "Cybercrime", "location": "Ahmedabad", "assigned_officer": "Officer A"})
    repository.add_evidence("CASE-OPS-1", {"evidence_type": "Image", "description": "Uploaded image", "file_reference": "uploads/evidence.jpg", "added_by": "Officer A"})
    assert len(repository.get_investigation_timeline("CASE-OPS-1")) == 2
    assert len(repository.get_evidence("CASE-OPS-1")) == 1
    alert = repository.create_alert({"alert_type": "SYSTEM", "severity": "HIGH", "message": "Review case", "source": "investigation"})
    assert repository.resolve_alert(alert["id"])["status"] == "RESOLVED"