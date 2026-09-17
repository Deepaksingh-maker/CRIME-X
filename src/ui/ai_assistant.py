"""Data-grounded deterministic AI assistant interface with voice dispatch system for police intelligence."""

from __future__ import annotations

import json
import streamlit as st

from src.services.ai_service import ask_crime_x
from src.services.tts_service import generate_voice_script, text_to_speech
from src.ui.components import page_header, section


def _render_browser_voice_dispatcher(script: str, auto_speak: bool = True, rate: float = 1.0, lang: str = "en-US") -> None:
    """Render interactive Web Speech API client component with automatic voice broadcast."""
    safe_script = json.dumps(script)
    safe_lang = json.dumps(lang)
    safe_auto = "true" if auto_speak else "false"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #cbd5e1;
      }}
      .voice-card {{
        background: linear-gradient(135deg, rgba(14, 25, 33, 0.95), rgba(10, 18, 24, 0.98));
        border: 1px solid #1f3744;
        border-left: 4px solid #59c68b;
        border-radius: 6px;
        padding: 10px 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
      }}
      .voice-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
      }}
      .voice-tag {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #59c68b;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }}
      .pulse-dot {{
        width: 8px;
        height: 8px;
        background-color: #59c68b;
        border-radius: 50%;
        box-shadow: 0 0 8px #59c68b;
        animation: pulse-ring 1.6s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
      }}
      @keyframes pulse-ring {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(89, 198, 139, 0.7); }}
        70% {{ transform: scale(1.15); box-shadow: 0 0 0 7px rgba(89, 198, 139, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(89, 198, 139, 0); }}
      }}
      .actions {{
        display: flex;
        gap: 6px;
        align-items: center;
      }}
      .btn {{
        background: #192d38;
        color: #e2e8f0;
        border: 1px solid #2d4c5c;
        border-radius: 4px;
        padding: 5px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }}
      .btn:hover {{
        background: #223f4f;
        border-color: #59c68b;
        color: #59c68b;
      }}
      .btn.stop {{
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.5);
        color: #fca5a5;
      }}
      .btn.stop:hover {{
        background: rgba(239, 68, 68, 0.3);
        color: #ffffff;
      }}
      .status-line {{
        margin-top: 6px;
        font-size: 0.75rem;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 6px;
      }}
      .wave-bars {{
        display: none;
        align-items: flex-end;
        gap: 2px;
        height: 12px;
      }}
      .wave-bars.active {{
        display: inline-flex;
      }}
      .bar {{
        width: 2.5px;
        background: #59c68b;
        border-radius: 1px;
        animation: sound-wave 0.7s ease-in-out infinite alternate;
      }}
      .bar:nth-child(1) {{ animation-delay: 0.1s; height: 6px; }}
      .bar:nth-child(2) {{ animation-delay: 0.3s; height: 12px; }}
      .bar:nth-child(3) {{ animation-delay: 0.2s; height: 8px; }}
      .bar:nth-child(4) {{ animation-delay: 0.4s; height: 10px; }}
      @keyframes sound-wave {{
        0% {{ height: 3px; }}
        100% {{ height: 12px; }}
      }}
    </style>
    </head>
    <body>
      <div class="voice-card">
        <div class="voice-top">
          <div class="voice-tag">
            <span class="pulse-dot"></span>
            <span>POLICE VOICE DISPATCH NARATION</span>
          </div>
          <div class="actions">
            <button class="btn" onclick="startSpeech()">🔊 Speak Briefing</button>
            <button class="btn stop" onclick="stopSpeech()">⏹ Stop</button>
          </div>
        </div>
        <div class="status-line">
          <div class="wave-bars" id="waveBars">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </div>
          <span id="speechStatus">Preparing speech engine...</span>
        </div>
      </div>

      <script>
        const textToNarrate = {safe_script};
        const autoPlay = {safe_auto};
        const voiceRate = {rate};
        const targetLang = {safe_lang};

        function getSynthesizer() {{
          try {{
            if (window.speechSynthesis) return window.speechSynthesis;
            if (window.parent && window.parent.speechSynthesis) return window.parent.speechSynthesis;
          }} catch(e) {{}}
          return null;
        }}

        function startSpeech() {{
          const synth = getSynthesizer();
          if (!synth) {{
            document.getElementById('speechStatus').innerText = "Browser speech synthesis unavailable.";
            return;
          }}

          synth.cancel();

          const utterance = new SpeechSynthesisUtterance(textToNarrate);
          utterance.rate = voiceRate;
          utterance.pitch = 1.0;
          utterance.lang = targetLang;

          const voices = synth.getVoices();
          if (voices && voices.length > 0) {{
            const langCode = targetLang.toLowerCase();
            const prefix = langCode.split('-')[0];
            const voiceMatch = voices.find(v => v.lang.toLowerCase() === langCode) ||
                               voices.find(v => v.lang.toLowerCase().startsWith(prefix));
            if (voiceMatch) utterance.voice = voiceMatch;
          }}

          const wave = document.getElementById('waveBars');
          const status = document.getElementById('speechStatus');

          utterance.onstart = () => {{
            wave.classList.add('active');
            status.innerHTML = '<span style="color:#59c68b;font-weight:600;">Broadcasting voice briefing out loud...</span>';
          }};

          utterance.onend = () => {{
            wave.classList.remove('active');
            status.innerHTML = '✓ Voice dispatch completed. Click "Speak Briefing" to replay.';
          }};

          utterance.onerror = (e) => {{
            wave.classList.remove('active');
            if (e.error === 'not-allowed') {{
              status.innerHTML = '<span style="color:#fbbf24;">Click "🔊 Speak Briefing" to activate audio.</span>';
            }} else {{
              status.innerHTML = 'Voice ready. Click "Speak Briefing" to play.';
            }}
          }};

          synth.speak(utterance);
        }}

        function stopSpeech() {{
          const synth = getSynthesizer();
          if (synth) synth.cancel();
          const wave = document.getElementById('waveBars');
          if (wave) wave.classList.remove('active');
          document.getElementById('speechStatus').innerHTML = 'Voice dispatch stopped.';
        }}

        if (autoPlay) {{
          setTimeout(startSpeech, 300);
        }} else {{
          document.getElementById('speechStatus').innerHTML = 'Voice ready. Click "🔊 Speak Briefing" to hear audio.';
        }}
      </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=88)


def _render_mic_transcriber() -> None:
    """Render client-side speech recognition widget that writes directly into the inquiry textarea."""
    mic_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      }
      .mic-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        height: 42px;
      }
      .mic-btn {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.18) 0%, rgba(14, 165, 233, 0.1) 100%);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 12px;
        padding: 9px 18px;
        font-size: 0.86rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        backdrop-filter: blur(12px);
        white-space: nowrap;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
      }
      .mic-btn:hover {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.3) 0%, rgba(14, 165, 233, 0.2) 100%);
        border-color: #38bdf8;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.3);
      }
      .mic-btn.listening {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border-color: #ef4444;
        color: #ffffff;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.6);
        animation: pulse-mic 1s infinite alternate;
      }
      @keyframes pulse-mic {
        0% { transform: scale(1); }
        100% { transform: scale(1.04); }
      }
      .mic-result {
        font-size: 0.74rem;
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        display: none;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 260px;
      }
    </style>
    </head>
    <body>
      <div class="mic-wrap">
        <button class="mic-btn" id="micBtn" onclick="toggleListening()">🎙️ Speak Inquiry (Voice-to-Text)</button>
        <span class="mic-result" id="micText"></span>
      </div>

      <script>
        let recognition = null;
        let isListening = false;

        function getSpeechRecognition() {
          const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
          if (!SpeechRec) return null;
          const rec = new SpeechRec();
          rec.continuous = false;
          rec.interimResults = true;
          rec.lang = 'en-IN';
          return rec;
        }

        function sendDirectlyToInput(text) {
          try {
            const parentDoc = window.parent.document;
            const textarea = parentDoc.querySelector('textarea[aria-label="Investigator Inquiry"]')
                          || parentDoc.querySelector('div[data-testid="stTextArea"] textarea')
                          || parentDoc.querySelector('textarea');
            if (textarea) {
              const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
              nativeSetter.call(textarea, text);
              textarea.dispatchEvent(new Event('input', { bubbles: true }));
              textarea.dispatchEvent(new Event('change', { bubbles: true }));
              textarea.focus();
            }
          } catch(e) {
            console.error("Parent DOM write error:", e);
          }
        }

        function toggleListening() {
          const btn = document.getElementById('micBtn');
          const resultBox = document.getElementById('micText');

          if (!recognition) {
            recognition = getSpeechRecognition();
            if (!recognition) {
              alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
              return;
            }

            recognition.onstart = () => {
              isListening = true;
              btn.classList.add('listening');
              btn.innerHTML = '🛑 Listening... Speak now';
              resultBox.style.display = 'inline-block';
              resultBox.innerText = 'Listening...';
            };

            recognition.onresult = (event) => {
              let transcript = '';
              for (let i = event.resultIndex; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
              }
              if (transcript.trim()) {
                sendDirectlyToInput(transcript);
                resultBox.style.display = 'inline-block';
                resultBox.innerText = '⚡ ' + transcript;
              }
            };

            recognition.onend = () => {
              isListening = false;
              btn.classList.remove('listening');
              btn.innerHTML = '🎙️ Speak Inquiry (Voice-to-Text)';
              resultBox.innerText = '✅ Speech captured into box!';
              setTimeout(() => { resultBox.style.display = 'none'; }, 2500);
            };

            recognition.onerror = (e) => {
              isListening = false;
              btn.classList.remove('listening');
              btn.innerHTML = '🎙️ Speak Inquiry (Voice-to-Text)';
              resultBox.innerText = 'Mic: ' + (e.error || 'error');
            };
          }

          if (isListening) {
            recognition.stop();
          } else {
            recognition.start();
          }
        }
      </script>
    </body>
    </html>
    """
    st.components.v1.html(mic_html, height=45)


def render(repository) -> None:
    page_header("CRIME X Intelligence Assistant", "Grounded queries on crime statistics, rankings, investigations, predictions, and GIS boundaries", "AI DISPATCH READY")

    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(13, 20, 36, 0.8), rgba(8, 14, 24, 0.95)); border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid #10b981; padding: 18px 22px; border-radius: 14px; margin-bottom: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:8px; height:8px; background:#10b981; border-radius:50%; box-shadow:0 0 8px #10b981;"></span>
                    <span style="color: #34d399; font-family:'JetBrains Mono', monospace; font-weight: 700; font-size: 0.82rem; letter-spacing:0.06em;">GROUNDED POLICE INTELLIGENCE ASSISTANT & VOICE SYSTEM</span>
                </div>
                <div style="display:inline-flex; align-items:center; gap:8px; background: rgba(16, 185, 129, 0.12); border:1px solid rgba(16, 185, 129, 0.4); color: #34d399; font-size: 0.72rem; padding: 4px 12px; border-radius: 20px; font-family:'JetBrains Mono', monospace; font-weight: 600;">
                    <div class="cx-audio-eq">
                        <span class="cx-eq-bar"></span>
                        <span class="cx-eq-bar"></span>
                        <span class="cx-eq-bar"></span>
                        <span class="cx-eq-bar"></span>
                        <span class="cx-eq-bar"></span>
                    </div>
                    <span>VOICE DISPATCH ACTIVE</span>
                </div>
            </div>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.84rem; line-height:1.5;">
                Connected to SQLite local datastore, NCRB 2022 historical snapshot, GIS administrative boundaries, and active case repositories. Equipped with real-time voice dispatch speech output and voice input recognition.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Voice Settings HUD
    with st.expander("⚙️ Voice Dispatch Settings & Controls", expanded=False):
        vcol1, vcol2, vcol3 = st.columns([1.5, 1.5, 1.5])
        with vcol1:
            auto_speak = st.toggle("🎙️ Auto-Speak on Query", value=True, help="Automatically narrate response when query completes")
        with vcol2:
            voice_rate = st.select_slider("Voice Speed", options=[0.8, 1.0, 1.2], value=1.0, format_func=lambda x: f"{x}x")
        with vcol3:
            voice_accent = st.selectbox(
                "Voice Accent",
                options=["Indian English (en-IN)", "Standard English (en-US)", "Hindi (hi-IN)"],
                index=0,
            )

    lang_map = {
        "Indian English (en-IN)": "en-IN",
        "Standard English (en-US)": "en-US",
        "Hindi (hi-IN)": "hi-IN",
    }
    selected_lang_code = lang_map.get(voice_accent, "en-IN")

    section("SUPPORTED INQUIRIES (ENGLISH & HINGLISH)")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.8; margin-bottom: 8px;">
            • <b>Rankings:</b> <i>"Which state has the highest crime?"</i> / <i>"India me sabse zyada crime kis state me hai?"</i><br>
            • <b>Cybercrime & Fraud:</b> <i>"Cyber fraud kaunsa highest hai?"</i> / <i>"Show cybercrime categories"</i><br>
            • <b>Cases & Alerts:</b> <i>"Kitne investigation open hain?"</i> / <i>"How many active alerts?"</i><br>
            • <b>Gujarat Series:</b> <i>"Gujarat me crime trend kya hai?"</i><br>
            • <b>GIS Map:</b> <i>"Crime map me kaunse states available hain?"</i><br>
            • <b>ML & Vision Models:</b> <i>"Crime prediction model kitna reliable hai?"</i> / <i>"Fire model ka result kya hai?"</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Inquiry Clickable Buttons for Easy Testing
    st.caption("Quick Inquiries:")
    pills = [
        "Kitne investigation open hain?",
        "Which state has the highest crime?",
        "How many active alerts?",
        "Cyber fraud kaunsa highest hai?",
        "Gujarat me crime trend kya hai?",
    ]
    p_cols = st.columns(len(pills))
    for idx, pill_text in enumerate(pills):
        if p_cols[idx].button(pill_text, key=f"quick_inq_{idx}"):
            st.session_state["inquiry_input"] = pill_text

    default_inquiry = st.session_state.get("inquiry_input", "")

    question = st.text_area(
        "Investigator Inquiry",
        value=default_inquiry,
        placeholder="Enter query in English or Hinglish (e.g. 'Kitne investigation open hain?' or 'Which state has highest crime?')...",
        height=85,
    )

    action_col1, action_col2 = st.columns([1.5, 3.5])
    with action_col1:
        submitted = st.button("Submit Inquiry", type="primary", use_container_width=True)
    with action_col2:
        _render_mic_transcriber()

    if submitted:
        if not question.strip():
            st.warning("Please enter a question or problem to submit.")
        else:
            try:
                result = ask_crime_x(question.strip(), repository=repository)
                spoken_script = generate_voice_script(result)

                section("ASSISTANT RESPONSE & VOICE DISPATCH")

                # 1. Spoken Audio Dispatch Bar
                _render_browser_voice_dispatcher(
                    script=spoken_script,
                    auto_speak=auto_speak,
                    rate=voice_rate,
                    lang=selected_lang_code,
                )

                # 2. Verbal Speech Script Quote Box
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, rgba(13,20,36,0.85), rgba(10,15,28,0.92)); border: 1px solid rgba(56,189,248,0.3); border-left: 4px solid #38bdf8; border-radius: 12px; padding: 14px 18px; margin: 14px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.3);">
                        <span style="font-family:'JetBrains Mono', monospace; font-size: 0.74rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing:0.06em;">🎙️ Verified Verbal Speech Script:</span>
                        <p style="font-size: 0.92rem; color: #ffffff; margin: 6px 0 0 0; font-style: italic; line-height:1.5;">
                            "{spoken_script}"
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 3. Native Audio Player Component
                with st.expander("🔊 Audio File Player & Download (.MP3)", expanded=False):
                    tts_result = text_to_speech(spoken_script, generate_audio=True)
                    if tts_result.get("audio"):
                        st.audio(tts_result["audio"], format=tts_result.get("mime_type", "audio/mp3"))
                        st.caption("Generated by CRIME X local voice synthesis engine.")
                    else:
                        st.caption("Local MP3 file generation offline; live browser Web Speech narration is active above.")

                # 4. Text Display of Grounded Intelligence Response
                if result.get("status") == "ok":
                    st.success(result["answer"])
                    st.caption(f"Source: {result.get('source', 'CRIME X Internal Services')} | Intent: {result.get('intent', 'general')}")
                else:
                    st.info(result.get("answer", "Data is not available in the current CRIME X database."))
                    st.caption(f"Status: Unavailable | Source: {result.get('source', 'CRIME X')} | Intent: {result.get('intent', 'unknown')}")

            except Exception as error:
                st.error(f"Error processing inquiry: {error}")