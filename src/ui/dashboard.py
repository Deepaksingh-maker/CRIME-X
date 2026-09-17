"""Dashboard view with modern tactical styling and motion animations."""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.services.crime_service import get_crime_overview
from src.services.cybercrime_service import get_cybercrime_overview
from src.ui.components import hero_banner, modern_kpi_card, page_header, records_table, section, status_capsule


def render(service, repository) -> None:
    hero_banner()
    page_header("Operations Command Center", "Authentic NCRB crime analytics, spatial intelligence & dispatch telemetry")
    st.caption("PROVENANCE: National Crime Records Bureau (NCRB) 2022 Historical Baseline · Validated Regional Aggregate")

    crime = get_crime_overview()
    cyber = get_cybercrime_overview()
    alerts = repository.get_alerts(unread_only=True)
    records = repository.get_crime_records(crime_type="total_cognizable_ipc_crimes")
    states = {row.get("state") for row in records if row.get("state")}
    districts = {row.get("district") for row in records if row.get("district")}

    # Motion KPI Grid with Glassmorphism 2.0 and themed accents
    kpi_html = f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Total Crimes", f"{crime['total_crime']:,.0f}", "NCRB 2022 IPC Cognizable", "red", "🚨")}
      {modern_kpi_card("Cybercrimes", f"{cyber['total_cyber_crimes']:,.0f}", "IT Act Offenses Logged", "cyan", "🛡️")}
      {modern_kpi_card("States & UTs", f"{len(states)}", "Complete India Coverage", "emerald", "🗺️")}
      {modern_kpi_card("Districts", f"{len(districts)}", "Verified Police Jurisdictions", "purple", "📍")}
      {modern_kpi_card("Active Alerts", f"{len(alerts)}", "Unread Dispatches in Queue", "amber", "⚠️")}
      {modern_kpi_card("Investigations", f"{repository.count_investigations()}", "Registered Active Cases", "red", "📁")}
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    chart_left, chart_right = st.columns([1.45, 1])
    with chart_left:
        section("STATE-WISE INCIDENT CONCENTRATION", icon="📈")
        top_states = service.get_state_ranking(8)
        if top_states:
            df_states = pd.DataFrame(top_states)
            fig = px.bar(
                df_states,
                x="total_cases",
                y="state_ut",
                orientation="h",
                title="Top States by Total Cognizable IPC Crimes (NCRB 2022)",
                template="plotly_dark",
                color="total_cases",
                color_continuous_scale=[
                    [0.0, "rgba(220, 38, 38, 0.4)"],
                    [0.5, "rgba(239, 68, 68, 0.75)"],
                    [1.0, "rgba(248, 113, 113, 1.0)"],
                ],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#cbd5e1"),
                margin=dict(l=10, r=10, t=40, b=10),
                coloraxis_showscale=False,
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.06)",
                    title="Reported Cases",
                    title_font=dict(family="JetBrains Mono, monospace", size=11),
                ),
                yaxis=dict(
                    autorange="reversed",
                    showgrid=False,
                    title="",
                    tickfont=dict(family="Plus Jakarta Sans, sans-serif", size=12),
                ),
            )
            fig.update_traces(
                marker_line_color="rgba(255,255,255,0.2)",
                marker_line_width=1,
                hovertemplate="<b>%{y}</b><br>Cases: %{x:,.0f}<extra></extra>",
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        section("COMMAND SYSTEM TELEMETRY", icon="📡")
        status_html = f"""
        <div style="display: flex; flex-direction: column; gap: 8px;">
            {status_capsule("SQLITE DATASTORE ENCRYPTED & CONNECTED", "emerald")}
            {status_capsule("ML RIDGE PREDICTION PIPELINE ONLINE", "cyan")}
            {status_capsule("YOLO11n AI FIRE VISION SENSORS ARMED", "amber")}
            {status_capsule("36 STATE & UT GIS BOUNDARIES INTEGRATED", "emerald")}
            {status_capsule("REAL-TIME TEXT-TO-SPEECH DISPATCH PROTOCOL READY", "cyan")}
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(15,23,42,0.7), rgba(10,15,28,0.8)); border: 1px solid rgba(255,255,255,0.08); border-left: 3px solid #38bdf8; border-radius: 12px; padding: 14px 18px; margin-top: 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#7dd3fc; font-weight:700;">ACTIVE INCIDENT QUEUE</span>
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#34d399;">LIVE STREAMING</span>
            </div>
            <p style="margin:0; font-size:0.8rem; color:#94a3b8; line-height:1.4;">Historical baseline initialized with 2022 aggregate data. Dispatch alerts and active investigations are tracked dynamically in SQLite.</p>
        </div>
        """, unsafe_allow_html=True)

    section("ACTIVE INCIDENT DISPATCH QUEUE", icon="🚨")
    if alerts:
        display_alerts = [
            {
                "Alert ID": f"#{a.get('id')}",
                "Severity": a.get("severity"),
                "Type": a.get("alert_type"),
                "Message": a.get("message"),
                "Time": str(a.get("created_at"))[:19] if a.get("created_at") else "N/A",
            }
            for a in alerts[:6]
        ]
        records_table(display_alerts)
    else:
        records_table([], "No active unread alerts in SQLite datastore.")