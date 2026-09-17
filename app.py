"""CRIME X police intelligence dashboard entry point."""

from __future__ import annotations

import streamlit as st
from sqlalchemy import func, select

from config import DATABASE_URL, SQLITE_PATH
from src.database.connection import create_db_engine, get_session_factory
from src.database.models import CrimeRecord
from src.database.repository import Repository
from src.database.schema import create_schema
from src.database.seed import seed_processed_data
from src.services.crime_x_service import CrimeXService
from src.ui import alerts, ai_assistant, crime_analysis, crime_map, crime_prediction, cybercrime, dashboard, fire_detection, investigations, settings
from src.ui.components import brand, inject_theme, render_page_transition


@st.cache_resource
def initialize_backend():
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_db_engine(DATABASE_URL)
    create_schema(engine)
    session = get_session_factory(DATABASE_URL)()
    if session.scalar(select(func.count()).select_from(CrimeRecord)) == 0:
        seed_processed_data(Repository(session))
    return session


def main() -> None:
    st.set_page_config(page_title="CRIME X | Police Intelligence", page_icon="🚨", layout="wide", initial_sidebar_state="expanded")
    inject_theme()

    nav_options = [
        "📊 Dashboard",
        "🔍 Crime Intelligence",
        "🗺️ Crime Map",
        "🔮 Crime Prediction",
        "💻 Cybercrime Intelligence",
        "🔥 Fire Detection",
        "📁 Cases & Investigation",
        "🚨 Alerts",
        "🎙️ AI Assistant",
        "⚙️ Settings",
    ]

    with st.sidebar:
        brand()
        selected_raw = st.radio("TACTICAL NAVIGATION", nav_options)
        navigation = selected_raw.split(" ", 1)[-1] if " " in selected_raw else selected_raw

        st.markdown(f"""
        <div style="margin-top: 24px; padding: 12px 14px; background: rgba(13,20,36,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#94a3b8; font-weight:700;">SQLITE DATABASE</span>
                <span style="display:inline-flex; align-items:center; gap:5px; font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#34d399;">
                    <span style="width:6px; height:6px; background:#10b981; border-radius:50%; box-shadow:0 0 6px #10b981;"></span>CONNECTED
                </span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.64rem; color:#64748b; margin-top:4px;">STORE: {SQLITE_PATH.name}</div>
        </div>
        """, unsafe_allow_html=True)

    if "current_nav" not in st.session_state:
        st.session_state.current_nav = navigation
    elif st.session_state.current_nav != navigation:
        st.session_state.current_nav = navigation
        render_page_transition(navigation)

    session = initialize_backend()
    repository = Repository(session)
    service = CrimeXService()
    views = {
        "Dashboard": lambda: dashboard.render(service, repository),
        "Crime Intelligence": lambda: crime_analysis.render(service),
        "Crime Map": lambda: crime_map.render(repository),
        "Crime Prediction": lambda: crime_prediction.render(service, repository),
        "Cybercrime Intelligence": lambda: cybercrime.render(service),
        "Fire Detection": lambda: fire_detection.render(service, repository),
        "Cases & Investigation": lambda: investigations.render(repository),
        "Alerts": lambda: alerts.render(repository),
        "AI Assistant": lambda: ai_assistant.render(repository),
        "Settings": lambda: settings.render(repository),
    }
    try:
        views[navigation]()
    except Exception as error:
        st.error("The selected module could not complete the request.")
        st.exception(error)


if __name__ == "__main__":
    main()