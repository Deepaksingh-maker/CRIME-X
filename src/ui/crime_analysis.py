"""Crime intelligence view with modern tactical styling and charts."""

import streamlit as st
import plotly.express as px
import pandas as pd

from src.services.crime_service import get_crime_overview
from src.ui.components import modern_kpi_card, page_header, records_table, section


def render(service) -> None:
    page_header("Crime Intelligence Analytics", "Explore, search, and analyze crime data across all Indian jurisdictions", "INTELLIGENCE RADAR ACTIVE")
    overview = get_crime_overview()
    states = service.get_state_ranking(20)

    top_state = states[0] if states else {"state_ut": "N/A", "total_cases": 0}

    st.markdown(f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Total Reported Crimes", f"{overview['total_crime']:,.0f}", "NCRB 2022 Baseline", "red", "🚨")}
      {modern_kpi_card("Highest Incident State", f"{top_state.get('state_ut')}", f"{top_state.get('total_cases', 0):,.0f} Reported Cases", "amber", "📍")}
      {modern_kpi_card("Active Jurisdictions", f"{len(states)} States/UTs", "Tracked in Crime Index", "cyan", "🏛️")}
    </div>
    """, unsafe_allow_html=True)

    section("STATE JURISDICTION RANKINGS", icon="📈")
    filter_left, filter_right = st.columns([1.5, 1])
    with filter_left:
        query = st.text_input("Search state or UT", key="crime_state_search", placeholder="e.g. Maharashtra, Uttar Pradesh...").strip().lower()
    with filter_right:
        sort_desc = st.toggle("Sort Highest First", value=True)

    filtered = [row for row in states if not query or query in str(row.get("state_ut", "")).lower()]
    filtered = sorted(filtered, key=lambda row: row.get("total_cases", 0), reverse=sort_desc)
    records_table(filtered)

    if filtered:
        df_filtered = pd.DataFrame(filtered)
        fig = px.bar(
            df_filtered,
            x="total_cases",
            y="state_ut",
            orientation="h",
            title="State Cognizable IPC Crime Volume (NCRB 2022)",
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
                title="Total Cases",
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

    section("DISTRICT HOTSPOT RANKING", icon="📍")
    district_query = st.text_input("Search district name", key="crime_district_search", placeholder="Filter by district name...").strip().lower()
    districts = service.get_district_ranking(30)
    records_table([row for row in districts if not district_query or district_query in str(row.get("district", "")).lower()])

    section("HISTORICAL DATA PROVENANCE", icon="📜")
    st.markdown('<div class="cx-note">Source: NCRB Table 1.1 · Reference year: 2022 · Granularity: State and district snapshots validated against official publication tables.</div>', unsafe_allow_html=True)
    st.caption("Provenance: National Crime Records Bureau (NCRB) Table 1.1, 2022. This is a verified historical aggregate snapshot.")