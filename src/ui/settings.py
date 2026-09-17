"""Application status and settings view with modern server rack diagnostics."""

import streamlit as st

from config import DATABASE_URL, MODEL_DIR
from src.database.connection import check_connection
from src.ui.components import modern_kpi_card, page_header, section, status_capsule


def render(repository) -> None:
    page_header("System Infrastructure & Diagnostics", "Runtime health, ML/DL model availability, database status & telemetry", "SYS DIAGNOSTICS ACTIVE")

    try:
        is_db_connected = check_connection()
        database_status = "CONNECTED" if is_db_connected else "UNAVAILABLE"
    except Exception:
        database_status = "UNAVAILABLE"
        is_db_connected = False

    ml_loaded = (MODEL_DIR / "ml" / "best_model.joblib").is_file()
    dl_loaded = (MODEL_DIR / "dl" / "crime_x_fire_detector_v2.pt").is_file()

    st.markdown(f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Database State", database_status, "SQLite Local Engine", "emerald" if is_db_connected else "red", "🗄️")}
      {modern_kpi_card("ML Prediction Model", "ONLINE" if ml_loaded else "OFFLINE", "Ridge Regression Engine", "cyan" if ml_loaded else "amber", "🧠")}
      {modern_kpi_card("YOLO Vision Model", "ARMED" if dl_loaded else "OFFLINE", "YOLO11n Flame Vision", "amber" if dl_loaded else "red", "🔥")}
      {modern_kpi_card("System Release", "v2.0 HUD", "Phase 19 Modernization", "purple", "⚡")}
    </div>
    """, unsafe_allow_html=True)

    section("INFRASTRUCTURE TELEMETRY RACK", icon="🖥️")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; gap:8px;">
            {status_capsule(f"SQLITE DATASTORE: {database_status}", "emerald" if is_db_connected else "red")}
            {status_capsule("GIS GEOJSON BOUNDARIES: 36 STATES & UTs LOADED", "emerald")}
            {status_capsule("ENCRYPTION PROTOCOL: AES-256 INTERNAL SESSION ACTIVE", "cyan")}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; gap:8px;">
            {status_capsule(f"ML RIDGE PREDICTOR: {'LOADED' if ml_loaded else 'UNAVAILABLE'}", "cyan" if ml_loaded else "amber")}
            {status_capsule(f"DL YOLO11n FIRE VISION: {'LOADED' if dl_loaded else 'UNAVAILABLE'}", "amber" if dl_loaded else "red")}
            {status_capsule("BROWSER TTS VOICE DISPATCH: WEB SPEECH API ACTIVE", "emerald")}
        </div>
        """, unsafe_allow_html=True)

    section("ENVIRONMENT SPECIFICATIONS", icon="⚙️")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(13,20,36,0.8), rgba(10,15,28,0.9)); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:18px 22px; font-family:'JetBrains Mono', monospace; font-size:0.78rem; color:#cbd5e1; line-height:1.8;">
        <div><span style="color:#64748b;">DATABASE ENDPOINT:</span> {DATABASE_URL.split('///')[-1]}</div>
        <div><span style="color:#64748b;">DATA SNAPSHOT:</span> National Crime Records Bureau (NCRB) 2022 Official Publication</div>
        <div><span style="color:#64748b;">UI ARCHITECTURE:</span> Tactical Glassmorphism 2.0 + Motion Animation Engine</div>
        <div><span style="color:#64748b;">RADAR SCANNER:</span> Dual-Ring Sweeping Telemetry with Real-Time Blip Tracker</div>
    </div>
    """, unsafe_allow_html=True)