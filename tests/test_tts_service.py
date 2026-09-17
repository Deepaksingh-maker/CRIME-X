import pytest
from src.services.tts_service import clean_text_for_speech, generate_voice_script, text_to_speech, synthesize_audio_bytes


def test_clean_text_for_speech():
    raw = "Rank | State | Total Crimes\n1 | Uttar Pradesh | 401,787\n2 | Maharashtra | 374,038"
    cleaned = clean_text_for_speech(raw)
    assert "Rank 1, Uttar Pradesh with 401,787 cases." in cleaned
    assert "Rank 2, Maharashtra with 374,038 cases." in cleaned
    assert "|" not in cleaned


def test_generate_voice_script_investigations():
    result = {"status": "ok", "intent": "investigations", "answer": "Investigations stored: 25\nOpen: 10"}
    script = generate_voice_script(result)
    assert "Case files found." in script
    assert "Investigations stored: 25" in script


def test_generate_voice_script_ranking():
    result = {
        "status": "ok",
        "intent": "state_ranking",
        "answer": "Rank | State | Total Crimes\n1 | Uttar Pradesh | 401,787",
    }
    script = generate_voice_script(result)
    assert "Case intelligence found." in script
    assert "Uttar Pradesh" in script


def test_generate_voice_script_unavailable():
    result = {"status": "unavailable", "intent": "unknown", "answer": "Data is not available in the current CRIME X database."}
    script = generate_voice_script(result)
    assert "No matching case" in script


def test_text_to_speech_default_mode():
    res = text_to_speech("Investigations stored: 5")
    assert res["status"] == "ready"
    assert res["audio"] is None
    assert "Case record found." in res["script"]


def test_text_to_speech_empty_raises_error():
    with pytest.raises(ValueError):
        text_to_speech("")


def test_text_to_speech_audio_generation():
    res = text_to_speech("Case file 101 registered", generate_audio=True)
    assert res["status"] in ("ok", "unavailable")
    assert res["script"] is not None
