"""Text-to-speech and voice briefing service for CRIME X AI Assistant."""

from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path


def clean_text_for_speech(text: str) -> str:
    """Strip table formatting, markdown symbols, and unpronounceable characters."""
    if not text:
        return ""
    # Replace markdown table rows like "1 | Uttar Pradesh | 401,787"
    lines = text.strip().split("\n")
    cleaned_lines: list[str] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("Rank |") or line.startswith("---") or line.startswith("==="):
            continue
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3:
                cleaned_lines.append(f"Rank {parts[0]}, {parts[1]} with {parts[2]} cases.")
            elif len(parts) == 2:
                cleaned_lines.append(f"{parts[0]}: {parts[1]}.")
            else:
                cleaned_lines.append(" ".join(parts))
        else:
            cleaned_lines.append(line)

    speech_text = " ".join(cleaned_lines)
    # Remove markdown bullets, bolding, italics, links
    speech_text = re.sub(r"[*_~`#]", "", speech_text)
    speech_text = re.sub(r"\s+", " ", speech_text).strip()
    return speech_text


def generate_voice_script(result: dict | str) -> str:
    """Generate a crisp, authoritative spoken briefing script for police intelligence."""
    if isinstance(result, str):
        cleaned = clean_text_for_speech(result)
        if not cleaned or "not available" in cleaned.lower() or "unavailable" in cleaned.lower():
            return "No matching case or crime record found in the CRIME X database."
        return f"Case record found. {cleaned}"

    if not isinstance(result, dict):
        return "No case information available."

    status = result.get("status")
    intent = result.get("intent", "general")
    raw_answer = str(result.get("answer", "")).strip()

    if status != "ok" or not raw_answer or "not available" in raw_answer.lower():
        return "No matching case or crime record found in the CRIME X database."

    cleaned_answer = clean_text_for_speech(raw_answer)

    # Intent-specific spoken headers
    if intent == "investigations":
        return f"Case files found. {cleaned_answer}"
    if intent in ("state_ranking", "district_ranking"):
        return f"Case intelligence found. Highest crime ranking summary: {cleaned_answer}"
    if intent == "alerts":
        return f"Security alerts found. {cleaned_answer}"
    if intent == "crime_overview":
        return f"Crime statistics found. {cleaned_answer}"
    if intent in ("cybercrime_overview", "cybercrime_categories", "fraud_analysis"):
        return f"Cybercrime intelligence found. {cleaned_answer}"
    if intent == "fire_detection_explanation":
        return f"Vision intelligence found. {cleaned_answer}"
    if intent == "gis_map":
        return f"GIS boundary records found. {cleaned_answer}"
    if intent == "crime_prediction":
        return f"Crime prediction model details found. {cleaned_answer}"
    if intent == "gujarat_analysis":
        return f"Gujarat crime records found. {cleaned_answer}"

    return f"Case intelligence found. {cleaned_answer}"


def synthesize_audio_bytes(text: str, lang: str = "en") -> tuple[bytes | None, str]:
    """Generate audio bytes using gTTS with offline pyttsx3 fallback."""
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return None, "empty_text"

    # 1. Try gTTS (Google Text-to-Speech) for high quality audio
    try:
        from gtts import gTTS

        # Use 150 words max for spoken audio payload
        truncated_text = " ".join(clean_text.split()[:120])
        tts = gTTS(text=truncated_text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read(), "audio/mp3"
    except Exception:
        pass

    # 2. Fallback: Try pyttsx3 (local Windows SAPI)
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        engine.save_to_file(clean_text[:500], tmp_path)
        engine.runAndWait()
        audio_data = Path(tmp_path).read_bytes()
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
        return audio_data, "audio/wav"
    except Exception:
        pass

    return None, "unavailable"


def text_to_speech(text: str, generate_audio: bool = False, lang: str = "en") -> dict[str, object]:
    """Provide speech script and optional synthesized audio payload."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must not be empty")

    script = generate_voice_script(text)

    if not generate_audio:
        # Default lightweight mode: provides formatted script for client-side Web Speech API
        return {
            "status": "ready",
            "audio": None,
            "script": script,
            "message": "Voice script ready for browser speech synthesis.",
        }

    audio_bytes, mime_type = synthesize_audio_bytes(script, lang=lang)
    if audio_bytes is not None:
        return {
            "status": "ok",
            "audio": audio_bytes,
            "mime_type": mime_type,
            "script": script,
            "message": "Audio synthesis complete.",
        }

    return {
        "status": "unavailable",
        "audio": None,
        "script": script,
        "message": "Local audio file synthesis unavailable; browser speech synthesis will be used.",
    }