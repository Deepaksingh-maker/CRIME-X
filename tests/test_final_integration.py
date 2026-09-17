"""Comprehensive end-to-end integration and quality assurance tests for Phase 18."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.database.repository import Repository
from src.gis.crime_map_service import CrimeMapService
from src.services.ai_service import ask_crime_x, detect_intent


def in_memory_repository() -> Repository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Repository(sessionmaker(bind=engine, expire_on_commit=False)())


# 1. Investigation Lifecycle (Create -> List -> Update -> Close -> Delete)
def test_investigation_full_lifecycle():
    repo = in_memory_repository()

    # Initial empty state
    assert repo.count_investigations() == 0
    assert repo.list_investigations() == []

    # CREATE
    created = repo.create_investigation({
        "case_reference": "CASE-2026-QA-01",
        "title": "Suspected Cyber Financial Fraud",
        "priority": "HIGH",
        "case_type": "Cybercrime",
        "location": "Ahmedabad",
        "assigned_officer": "Inspector V. Patel",
        "description": "Unauthorized bank fund transfers reported via phishing",
    })
    assert created["case_reference"] == "CASE-2026-QA-01"
    assert created["status"] == "OPEN"
    assert repo.count_investigations(status="OPEN") == 1

    # LIST & SEARCH
    found_cases = repo.list_investigations(search="Ahmedabad")
    assert len(found_cases) == 1
    assert found_cases[0]["case_reference"] == "CASE-2026-QA-01"

    # UPDATE to INVESTIGATING
    repo.update_investigation("CASE-2026-QA-01", {"status": "INVESTIGATING"})
    updated = repo.get_investigation("CASE-2026-QA-01")
    assert updated["status"] == "INVESTIGATING"

    # CLOSE
    repo.update_investigation("CASE-2026-QA-01", {"status": "CLOSED"})
    closed = repo.get_investigation("CASE-2026-QA-01")
    assert closed["status"] == "CLOSED"

    # DELETE
    deleted = repo.delete_investigation("CASE-2026-QA-01")
    assert deleted is True
    assert repo.count_investigations() == 0
    assert repo.get_investigation("CASE-2026-QA-01") is None


# 2. Alert Lifecycle (Create -> List -> Mark Read -> Resolve -> Delete)
def test_alert_full_lifecycle():
    repo = in_memory_repository()

    assert repo.get_alerts() == []

    # CREATE
    alert = repo.create_alert({
        "alert_type": "HIGH_RISK_DISTRICT",
        "severity": "CRITICAL",
        "message": "Spike in theft incidents reported in sector",
        "source": "automated_monitor",
    })
    alert_id = alert["id"]
    assert alert["status"] == "UNREAD"
    assert alert["is_read"] is False

    # UNREAD LIST
    unread = repo.get_alerts(unread_only=True)
    assert len(unread) == 1

    # MARK READ
    repo.mark_alert_read(alert_id)
    read_alert = [a for a in repo.get_alerts() if a["id"] == alert_id][0]
    assert read_alert["is_read"] is True
    assert read_alert["status"] == "READ"

    # RESOLVE
    repo.resolve_alert(alert_id)
    resolved_alert = [a for a in repo.get_alerts() if a["id"] == alert_id][0]
    assert resolved_alert["status"] == "RESOLVED"

    # DELETE
    assert repo.delete_alert(alert_id) is True
    assert repo.get_alerts() == []


# 3. Grounded AI Assistant Answers to Target Queries
def test_ai_assistant_target_queries():
    repo = in_memory_repository()
    # Add a mock open investigation to verify live count
    repo.create_investigation({"case_reference": "CASE-AI-TEST", "title": "Test case", "status": "OPEN"})

    # Query 1: Highest crime state (Hinglish)
    q1 = ask_crime_x("India me sabse zyada crime kis state me hai?", repository=repo)
    assert q1["status"] == "ok"
    assert "Uttar Pradesh" in q1["answer"]
    assert "NCRB" in q1["source"]

    # Query 2: Cyber fraud ranking (Hinglish)
    q2 = ask_crime_x("Cyber fraud kaunsa highest hai?", repository=repo)
    assert q2["status"] == "ok"
    assert len(q2["answer"]) > 0

    # Query 3: Open investigations count (Hinglish)
    q3 = ask_crime_x("Kitne investigation open hain?", repository=repo)
    assert q3["status"] == "ok"
    assert "Open: 1" in q3["answer"]

    # Query 4: Gujarat crime trend
    q4 = ask_crime_x("Gujarat me crime trend kya hai?", repository=repo)
    assert q4["status"] == "ok"
    assert "2018" in q4["answer"] or "2014" in q4["answer"]

    # Query 5: Available states in Crime Map
    q5 = ask_crime_x("Crime map me kaunse states available hain?", repository=repo)
    assert q5["status"] == "ok"
    assert "36" in q5["answer"]
    assert "GeoJSON" in q5["source"]

    # Query 6: Fire model result
    q6 = ask_crime_x("Fire model ka result kya hai?", repository=repo)
    assert q6["status"] == "ok"
    assert ("experimental" in q6["answer"].lower() or "no fire detection history" in q6["answer"].lower())

    # Query 7: Prediction model reliability
    q7 = ask_crime_x("Crime prediction model kitna reliable hai?", repository=repo)
    assert q7["status"] == "ok"
    assert "decision-support" in q7["answer"].lower()
    assert "unavailable" in q7["answer"].lower()

    # Query 8: Unsupported inquiry guarantees zero hallucination
    q8 = ask_crime_x("Tell me fictional crimes in Atlantis")
    assert q8["status"] == "unavailable"
    assert "not available" in q8["answer"].lower()


# 4. GIS Map Integration and Data Provenance
def test_gis_map_aggregation_and_provenance():
    service = CrimeMapService()

    # State physical crime
    df_state = service.aggregate_crime_data(mode="Physical Crime", level="state", year=2022)
    assert len(df_state) == 36
    assert all(df_state["source"] == "NCRB 2022 (Historical Data)")
    assert all(df_state["year"] == 2022)

    # Cybercrime aggregation
    df_cyber = service.aggregate_crime_data(mode="Cybercrime", level="state", year=2022)
    assert len(df_cyber) == 36
    assert all(df_cyber["source"] == "NCRB 2022 (Historical Data)")

    # Diagnostics
    diag = service.get_diagnostics(df_state)
    assert diag["matched"] == 36
    assert diag["unmatched"] == 0


# 5. UI Disclaimer and Honest Framing Assertions
def test_ui_claims_contain_no_false_marketing():
    from pathlib import Path

    ui_dir = Path("src/ui")
    forbidden_claims = [
        "fire and smoke detection",
        "fire & smoke detection",
        "live crime reporting",
        "100% accurate",
        "guaranteed prediction",
    ]

    for py_file in ui_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8").lower()
        for forbidden in forbidden_claims:
            assert forbidden not in content, f"Found misleading phrase '{forbidden}' in {py_file.name}"
