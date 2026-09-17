"""Crime prediction view with modern ML diagnostic interface."""

import streamlit as st

from src.ui.components import modern_kpi_card, page_header, section


def render(service, repository=None) -> None:
    page_header("Predictive Crime Intelligence", "Machine learning regression models for future incident count estimates", "ML PIPELINE ARMED")

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(20, 32, 48, 0.75), rgba(13, 20, 32, 0.9)); border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid #38bdf8; border-radius: 14px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-family:'Outfit', sans-serif; font-weight:700; font-size:1rem; color:#f8fafc;">
                🤖 Academic Machine Learning Decision-Support Engine
            </div>
            <span style="font-family:'JetBrains Mono', monospace; font-size:0.74rem; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.4); padding:3px 10px; border-radius:20px; color:#7dd3fc; font-weight:600;">
                MODEL: RIDGE REGRESSION
            </span>
        </div>
        <p style="margin:6px 0 0 0; color:#94a3b8; font-size:0.84rem; line-height:1.5;">
            Trained on historical NCRB longitudinal tables. Provides macro-level academic trend estimation for administrative decision support. This is not an individual risk assessment or deterministic guarantee of crime.
        </p>
    </div>
    """, unsafe_allow_html=True)

    section("HISTORICAL INPUT PARAMETERS", icon="⚙️")
    col1, col2, col3 = st.columns(3)
    with col1:
        first = st.number_input("Lag 2020 Crime Count", min_value=0.0, value=100.0, help="Historical reported cognizable IPC crimes in base year 2020")
    with col2:
        second = st.number_input("Lag 2021 Crime Count", min_value=0.0, value=90.0, help="Historical reported cognizable IPC crimes in preceding year 2021")
    with col3:
        population = st.number_input("Estimated Population (Lakhs)", min_value=0.0, value=500.0, help="Jurisdiction population baseline in lakhs (1 lakh = 100,000)")

    if st.button("Generate ML Risk Estimate", type="primary"):
        result = service.predict_crime_count({"lag_2020_count": first, "lag_2021_count": second, "population_2022_lakhs": population})
        if repository is not None:
            repository.save_prediction({**result, "input_features": {"lag_2020_count": first, "lag_2021_count": second, "population_2022_lakhs": population}})

        section("MODEL INFERENCE OUTPUT", icon="📊")
        st.markdown(f"""
        <div class="cx-kpi-grid">
          {modern_kpi_card("Predicted Incident Volume", f"{result['predicted_count']:,.2f}", "Estimated Annual Incidents", "red", "🔮")}
          {modern_kpi_card("Active Model", f"{result['model']}", "Regularized Linear Baseline", "cyan", "🧠")}
          {modern_kpi_card("Population Normalizer", f"{population:,.0f} L", "Baseline Denominator", "emerald", "👥")}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.08); border-left: 3px solid #f59e0b; border-radius: 12px; padding: 14px 18px; margin-top: 14px;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#fbbf24; font-weight:700; text-transform:uppercase;">MODEL VALIDATION NOTE:</div>
            <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.84rem; line-height:1.5;">{result['warning']}</p>
            <div style="margin-top:6px; font-family:'JetBrains Mono', monospace; font-size:0.72rem; color:#64748b;">Confidence bounds: Unavailable due to sample constraints in historical NCRB longitudinal tables.</div>
        </div>
        """, unsafe_allow_html=True)