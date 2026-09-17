"""Cybercrime intelligence view with modern tactical styling and charts."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ui.components import modern_kpi_card, page_header, records_table, section


def render(service) -> None:
    page_header("Cybercrime Intelligence", "Digital threat vectors, IT Act offences, state rankings & fraud telemetry", "CYBER SENSORS ACTIVE")
    overview = service.get_cybercrime_overview()
    categories = service.get_cybercrime_categories()
    fraud_data = service.get_fraud_analysis()

    st.markdown(f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Total Cybercrimes", f"{overview['total_cyber_crimes']:,.0f}", "NCRB IT Act Offences", "cyan", "🛡️")}
      {modern_kpi_card("Districts Reporting", f"{len(overview.get('district_ranking', []))}", "Regional Coverage", "purple", "📍")}
      {modern_kpi_card("Crime Categories", f"{len(categories)}", "Tracked Attack Modalities", "amber", "⚡")}
      {modern_kpi_card("Fraud Types", f"{len(fraud_data)}", "Financial & Identity Fraud", "red", "💳")}
    </div>
    """, unsafe_allow_html=True)

    section("STATE & UT CYBER INCIDENT RANKINGS", icon="📊")
    search = st.text_input("Search jurisdiction name", placeholder="Filter by state or UT...").strip().lower()
    records_table([row for row in overview["state_ranking"] if not search or search in str(row).lower()])

    section("CYBERCRIME ATTACK VECTOR DISTRIBUTION", icon="💻")
    if categories:
        df_cat = pd.DataFrame(categories)
        fig = px.bar(
            df_cat,
            x="category",
            y="total_cases",
            title="Cybercrime Incident Distribution by Category (NCRB 2022)",
            template="plotly_dark",
            color="total_cases",
            color_continuous_scale=[
                [0.0, "rgba(56, 189, 248, 0.4)"],
                [0.5, "rgba(56, 189, 248, 0.8)"],
                [1.0, "rgba(129, 140, 248, 1.0)"],
            ],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#cbd5e1"),
            margin=dict(l=10, r=10, t=40, b=10),
            coloraxis_showscale=False,
            xaxis=dict(
                showgrid=False,
                title="",
                tickangle=-25,
                tickfont=dict(family="Plus Jakarta Sans, sans-serif", size=11),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                title="Reported Incidents",
                title_font=dict(family="JetBrains Mono, monospace", size=11),
            ),
        )
        fig.update_traces(
            marker_line_color="rgba(255,255,255,0.2)",
            marker_line_width=1,
            hovertemplate="<b>%{x}</b><br>Incidents: %{y:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig, use_container_width=True)
        records_table(categories)

    section("FRAUD & FINANCIAL CYBERCRIME ANALYSIS", icon="💰")
    records_table(fraud_data)
    st.caption("Historical NCRB aggregate data · Validated baseline for academic decision support · Not a live real-time fraud dispatch.")