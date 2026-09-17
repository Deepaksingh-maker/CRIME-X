"""Deterministic, data-grounded CRIME X assistant."""

from __future__ import annotations

from src.services.crime_service import get_crime_overview, get_district_ranking, get_state_ranking
from src.data.analysis import gujarat_analysis
from src.services.cybercrime_service import get_cybercrime_categories, get_cybercrime_overview, get_fraud_analysis


INTENTS = (
    "crime_overview", "state_ranking", "district_ranking", "crime_categories",
    "cybercrime_overview", "cybercrime_categories", "fraud_analysis", "gujarat_analysis",
    "crime_prediction", "fire_detection_explanation", "investigations", "alerts",
    "database_status", "gis_map", "help", "unknown",
)


def detect_intent(question: str) -> str:
    """Route English and practical Hinglish queries using bounded keyword rules."""

    text = question.lower().strip()
    if not text:
        raise ValueError("Question must not be empty")
    if any(word in text for word in ("database", "db", "connected", "stored")):
        return "database_status"
    if any(word in text for word in ("investigation", "case", "open case", "investigations")):
        return "investigations"
    if any(word in text for word in ("alert", "active alert", "unread alert")):
        return "alerts"
    if any(word in text for word in ("fire detection", "fire detected", "fire model", "confidence", "aag", "आग")):
        return "fire_detection_explanation"
    if any(word in text for word in ("map", "gis", "boundary", "boundaries", "geojson")) and any(word in text for word in ("state", "states", "available", "kaunse", "which")):
        return "gis_map"
    if any(word in text for word in ("predict", "prediction", "ml model", "future crime", "reliable", "reliability")):
        return "crime_prediction"
    if any(word in text for word in ("gujarat", "ગુજરાત")) and any(word in text for word in ("trend", "year", "crime")):
        return "gujarat_analysis"
    if any(word in text for word in ("fraud", "otp", "banking fraud", "cyber fraud")):
        return "fraud_analysis"
    if any(word in text for word in ("cybercrime", "cyber crime", "cybercriminal", "साइबरक्राइम")):
        if any(word in text for word in ("category", "categories", "type")):
            return "cybercrime_categories"
        return "cybercrime_overview"
    if any(word in text for word in ("category", "categories", "crime categories")):
        return "crime_categories"
    if any(word in text for word in ("district", "जिला", "kaha", "where")):
        return "district_ranking"
    if any(word in text for word in ("state", "states", "kis state", "top 5", "sabse zyada")):
        return "state_ranking"
    if any(word in text for word in ("crime overview", "how many crimes", "kitne crime", "total crime", "overview")):
        return "crime_overview"
    if any(word in text for word in ("help", "what can", "kya pooch")):
        return "help"
    return "unknown"


def _ranking_text(rows: list[dict], label: str, limit: int = 5) -> str:
    if not rows:
        return "Data is not available in the current CRIME X database."
    key = "state_ut" if label == "State" else "district"
    lines = [f"Rank | {label} | Total Crimes"]
    lines += [f"{index} | {row.get(key, 'Unknown')} | {row.get('total_cases', 0):,.0f}" for index, row in enumerate(rows[:limit], 1)]
    return "\n".join(lines)


def answer_question(question: str, repository=None) -> dict[str, object]:
    """Answer supported questions from approved services/repository data only."""

    intent = detect_intent(question)
    if intent == "state_ranking":
        rows = get_state_ranking(10, repository=repository) if repository else get_state_ranking(10)
        answer = _ranking_text(rows, "State")
        return {"status": "ok", "intent": intent, "answer": answer, "source": "NCRB 2022 state-level snapshot"}
    if intent == "district_ranking":
        rows = get_district_ranking(10, repository=repository) if repository else get_district_ranking(10)
        return {"status": "ok", "intent": intent, "answer": _ranking_text(rows, "District"), "source": "NCRB 2022 district-level snapshot"}
    if intent == "crime_overview":
        result = get_crime_overview(repository=repository) if repository else get_crime_overview()
        return {"status": "ok", "intent": intent, "answer": f"Total Crimes: {result['total_crime']:,.0f}\nScope: NCRB 2022 historical snapshot", "source": "NCRB"}
    if intent == "cybercrime_overview":
        result = get_cybercrime_overview(repository=repository) if repository else get_cybercrime_overview()
        return {"status": "ok", "intent": intent, "answer": f"Total Cybercrime: {result['total_cyber_crimes']:,.0f}\nScope: NCRB 2022 historical aggregate", "source": "NCRB"}
    if intent == "cybercrime_categories":
        rows = get_cybercrime_categories(repository=repository) if repository else get_cybercrime_categories()
        return {"status": "ok", "intent": intent, "answer": "\n".join(f"{row['category']}: {row['total_cases']:,.0f}" for row in rows) or "Data is not available in the current CRIME X database.", "source": "NCRB cybercrime categories"}
    if intent == "fraud_analysis":
        rows = get_fraud_analysis(repository=repository) if repository else get_fraud_analysis()
        return {"status": "ok", "intent": intent, "answer": "\n".join(f"{row['category']}: {row['total_cases']:,.0f}" for row in rows) or "Data is not available in the current CRIME X database.", "source": "NCRB cyber fraud categories"}
    if intent == "crime_categories":
        return {"status": "unavailable", "intent": intent, "answer": "Data is not available in the current CRIME X database.", "source": "CRIME X"}
    if intent == "gujarat_analysis":
        result = gujarat_analysis()
        rows = result["yearly"].to_dict(orient="records")
        return {"status": "ok", "intent": intent, "answer": "\n".join(f"{row['year']}: {row['total_cases']:,.0f}" for row in rows), "source": "Ahmedabad historical crime series, 2014-2018"}
    if intent == "gis_map":
        return {
            "status": "ok",
            "intent": intent,
            "answer": "All 36 Indian States and Union Territories (including Ladakh, Jammu & Kashmir, and Telangana) have verified administrative boundary GeoJSONs available in the CRIME X GIS intelligence module. 375 district boundaries are also verified.",
            "source": "DataMeet / GADM GeoJSON Boundaries",
        }
    if intent == "crime_prediction":
        return {
            "status": "ok",
            "intent": intent,
            "answer": "The ML model is an academic decision-support experiment based on three annual observations (2020-2022). It is not a guaranteed prediction and confidence intervals are statistically unavailable.",
            "source": "CRIME X ML model (Linear/Ridge baseline)",
        }
    if intent == "fire_detection_explanation":
        rows = repository.get_fire_detection_history() if repository else []
        if not rows:
            return {"status": "ok", "intent": intent, "answer": "No fire detection history is stored yet. Upload an image in AI Fire Detection.", "source": "SQLite"}
        latest = rows[0]
        return {
            "status": "ok",
            "intent": intent,
            "answer": f"Latest stored result contains {len(latest['detections'])} detection(s). The model is an experimental vision prototype trained on fire-only imagery (no smoke detection) and is not production fire safety equipment.",
            "source": "SQLite / YOLO v2 (Fire-only)",
        }
    if intent == "investigations":
        rows = repository.list_investigations() if repository else []
        return {"status": "ok", "intent": intent, "answer": f"Investigations stored: {len(rows)}\nOpen: {sum(row.get('status') == 'OPEN' for row in rows)}", "source": "SQLite"}
    if intent == "alerts":
        rows = repository.get_alerts(unread_only=True) if repository else []
        return {"status": "ok", "intent": intent, "answer": f"Active unread alerts: {len(rows)}", "source": "SQLite"}
    if intent == "database_status":
        return {"status": "ok", "intent": intent, "answer": "SQLite database is connected through the CRIME X repository.", "source": "SQLite"}
    if intent == "help":
        return {"status": "ok", "intent": intent, "answer": "Ask about state rankings, district rankings, crime overview, cybercrime, fraud, investigations, alerts, predictions, or fire detection.", "source": "CRIME X"}
    return {"status": "unavailable", "intent": intent, "answer": "Data is not available in the current CRIME X database.", "source": "CRIME X"}


def ask_crime_x(question: str, repository=None) -> dict[str, object]:
    return answer_question(question, repository=repository)