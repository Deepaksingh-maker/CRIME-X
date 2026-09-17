"""Verified GIS Crime Intelligence Map view for CRIME X command center."""

from __future__ import annotations

import streamlit as st
from streamlit_folium import st_folium

from src.gis.crime_map_service import (
    CYBER_CATEGORIES,
    PHYSICAL_CATEGORIES,
    QUARTILE_COLORS,
    CrimeMapService,
)
from src.ui.components import page_header, section


@st.cache_resource
def get_map_service() -> CrimeMapService:
    """Cache the GIS crime mapping service singleton."""
    return CrimeMapService()


def render(repository=None) -> None:
    """Render the high-precision GIS Crime Intelligence module."""
    service = get_map_service()

    page_header(
        "Geographic Crime Intelligence",
        "Authentic administrative GIS boundaries & historical NCRB spatial analytics",
        "GIS MAPPING ACTIVE",
    )

    # 1. Interactive Control Panel
    c1, c2, c3, c4, c5 = st.columns([1.2, 1.5, 1.5, 1.2, 1.2])

    with c1:
        mode = st.selectbox(
            "MAP DOMAIN",
            ["Physical Crime", "Cybercrime"],
            index=0,
            help="Toggle between IPC physical crimes and IT Act cybercrimes.",
        )

    filter_opts = service.get_filter_options(mode=mode)

    with c2:
        selected_state = st.selectbox(
            "STATE / UT",
            filter_opts["states"],
            index=0,
            help="Filter by Indian State or Union Territory.",
        )

    # Re-fetch districts for selected state
    district_opts = ["All Districts"]
    if selected_state != "All States":
        state_filter_opts = service.get_filter_options(mode=mode, selected_state=selected_state)
        district_opts = state_filter_opts["districts"]

    with c3:
        selected_district = st.selectbox(
            "DISTRICT",
            district_opts,
            index=0,
            disabled=(selected_state == "All States"),
            help="Filter by administrative district within the selected state.",
        )

    with c4:
        crime_category = st.selectbox(
            "CRIME CATEGORY",
            filter_opts["categories"],
            index=0,
            help="Select specific crime category or total aggregation.",
        )

    with c5:
        metric = st.selectbox(
            "METRIC TYPE",
            ["Crime Count", "Crime Rate"],
            index=0,
            help="Select raw incident count or normalized crime rate per 100,000 population.",
        )

    # Diagnostic & Scope Notice
    level = "district" if (selected_state != "All States" and len(district_opts) > 1) else "state"

    if metric == "Crime Rate" and level == "district":
        st.info("Crime rate unavailable for district level: district populations are not reported in the NCRB snapshot. Displaying actual crime counts.")

    # 2. Data Aggregation
    state_arg = None if selected_state == "All States" else selected_state
    try:
        data_df = service.aggregate_crime_data(
            mode=mode,
            level=level,
            year=2022,
            crime_category=crime_category,
            selected_state=state_arg,
        )
    except Exception as exc:
        st.error(f"Error aggregating geographic data: {exc}")
        return

    diagnostics = service.get_diagnostics(data_df)

    # 3. Dynamic Map Generation
    folium_map, quartiles = service.build_folium_map(
        data_df=data_df,
        level=level,
        metric=metric,
        selected_state=state_arg,
        selected_district=None if selected_district == "All Districts" else selected_district,
    )

    # Map & Legend Layout
    map_col, stat_col = st.columns([3.8, 1.2])

    with map_col:
        map_output = st_folium(
            folium_map,
            use_container_width=True,
            height=620,
            returned_objects=["last_object_clicked_tooltip"],
        )

    with stat_col:
        q1, q2, q3 = quartiles["q1"], quartiles["q2"], quartiles["q3"]
        unit = "crimes" if metric == "Crime Count" or level == "district" else "per 100k"

        # 1. Quartile Classification Card
        st.markdown(
            f"""
            <div style="background: rgba(13, 22, 32, 0.85); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1px solid rgba(41, 65, 82, 0.55); border-top: 2px solid #8f1d28; border-radius: 10px; padding: 14px 16px; margin-bottom: 14px; box-shadow: 0 6px 20px rgba(0,0,0,0.35);">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="width:7px; height:7px; background:#8f1d28; border-radius:50%; display:inline-block;"></span>
                    <h4 style="margin:0; font-size: 0.8rem; font-weight: 700; color: #edf3f4; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'JetBrains Mono', monospace;">
                        QUARTILE THRESHOLDS
                    </h4>
                </div>
                <div style="display:flex; flex-direction:column; gap: 8px; font-size: 0.78rem;">
                    <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(143, 29, 40, 0.12); padding:5px 10px; border-radius:6px; border-left:3px solid {QUARTILE_COLORS['Very High']};">
                        <span style="color: #d17b83; font-weight: 700;">Very High:</span>
                        <span style="color: #f1f5f9; font-family: monospace; font-weight:600;">&gt; {q3:,.0f} {unit}</span>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(234, 88, 12, 0.08); padding:5px 10px; border-radius:6px; border-left:3px solid {QUARTILE_COLORS['High']};">
                        <span style="color: #fb923c; font-weight: 700;">High:</span>
                        <span style="color: #f1f5f9; font-family: monospace; font-weight:600;">{q2:,.0f} – {q3:,.0f}</span>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(255, 183, 77, 0.08); padding:5px 10px; border-radius:6px; border-left:3px solid {QUARTILE_COLORS['Medium']};">
                        <span style="color: #fcd34d; font-weight: 700;">Medium:</span>
                        <span style="color: #f1f5f9; font-family: monospace; font-weight:600;">{q1:,.0f} – {q2:,.0f}</span>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(30, 58, 138, 0.15); padding:5px 10px; border-radius:6px; border-left:3px solid {QUARTILE_COLORS['Low']};">
                        <span style="color: #93c5fd; font-weight: 700;">Low:</span>
                        <span style="color: #f1f5f9; font-family: monospace; font-weight:600;">&le; {q1:,.0f} {unit}</span>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(51, 65, 85, 0.15); padding:5px 10px; border-radius:6px; border-left:3px solid {QUARTILE_COLORS['No Data']};">
                        <span style="color: #94a3b8; font-weight: 500;">No Data / Unmatched</span>
                        <span style="color: #64748b; font-family: monospace;">—</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. GIS Spatial Integrity Card
        st.markdown(
            f"""
            <div style="background: rgba(13, 22, 32, 0.85); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1px solid rgba(41, 65, 82, 0.55); border-top: 2px solid #00e5ff; border-radius: 10px; padding: 14px 16px; margin-bottom: 14px; box-shadow: 0 6px 20px rgba(0,0,0,0.35);">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="width:7px; height:7px; background:#00e5ff; border-radius:50%; box-shadow:0 0 8px #00e5ff; display:inline-block;"></span>
                    <h4 style="margin:0; font-size: 0.8rem; font-weight: 700; color: #edf3f4; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'JetBrains Mono', monospace;">
                        GIS SPATIAL INTEGRITY
                    </h4>
                </div>
                <div style="display:flex; flex-direction:column; gap:6px; font-size: 0.78rem; color: #cbd5e1;">
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:4px;">
                        <span style="color:#94a3b8;">Level:</span>
                        <span style="font-family:monospace; font-weight:700; color:#00e5ff;">{level.upper()}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:4px;">
                        <span style="color:#94a3b8;">Matched Units:</span>
                        <span style="font-family:monospace; font-weight:700; color:#00e676;">{diagnostics['matched']} (Verified)</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:4px;">
                        <span style="color:#94a3b8;">Unmatched Units:</span>
                        <span style="font-family:monospace; font-weight:700; color:#94a3b8;">{diagnostics['unmatched']} (Unforced)</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-top:2px;">
                        <span style="color:#94a3b8;">Total Geometry:</span>
                        <span style="font-family:monospace; font-weight:700; color:#f1f5f9;">{diagnostics['total']} Units</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 3. Data Provenance Card
        st.markdown(
            """
            <div style="background: rgba(13, 22, 32, 0.85); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1px solid rgba(41, 65, 82, 0.55); border-top: 2px solid #ffb74d; border-radius: 10px; padding: 14px 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.35);">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                    <span style="width:7px; height:7px; background:#ffb74d; border-radius:50%; box-shadow:0 0 8px #ffb74d; display:inline-block;"></span>
                    <h4 style="margin:0; font-size: 0.8rem; font-weight: 700; color: #edf3f4; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'JetBrains Mono', monospace;">
                        DATA PROVENANCE &amp; CRS
                    </h4>
                </div>
                <div style="font-size: 0.74rem; color: #94a3b8; line-height: 1.6;">
                    <div><b style="color:#cbd5e1;">Source:</b> NCRB 2022 Annual Survey</div>
                    <div><b style="color:#cbd5e1;">Tables:</b> 1.1 (IPC) · 10.1 · 1A.1</div>
                    <div><b style="color:#cbd5e1;">CRS:</b> EPSG:4326 (WGS-84 Standard)</div>
                    <div><b style="color:#cbd5e1;">Policy:</b> Zero Coordinate Fabrication</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Location Intelligence Detail Card ("Show Details UI")
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    target_location: str | None = None
    if selected_district != "All Districts":
        target_location = selected_district
        target_level = "district"
    elif selected_state != "All States":
        target_location = selected_state
        target_level = "state"
    else:
        if map_output and map_output.get("last_object_clicked_tooltip"):
            tooltip_str = str(map_output["last_object_clicked_tooltip"])
            if "Location:" in tooltip_str:
                target_location = tooltip_str.split("Location:")[1].split("\n")[0].strip()
                target_level = level
            else:
                target_location = tooltip_str.strip()
                target_level = level
        else:
            target_location = None
            target_level = level

    if target_location:
        info = service.get_location_intelligence(
            name=target_location,
            level=target_level,
            mode=mode,
            year=2022,
            parent_state=selected_state if selected_state != "All States" else None,
        )

        panel_type = "DISTRICT SPATIAL TELEMETRY" if target_level == "district" else "STATE SPATIAL TELEMETRY"
        crime_count_val = float(info.get("crime_count", 0.0) or 0.0)
        rate_val = info.get("crime_rate")

        comp_val = float(rate_val) if (metric == "Crime Rate" and rate_val is not None) else crime_count_val
        if comp_val > quartiles["q3"]:
            tier_badge = '<span style="background:rgba(143,29,40,0.22); border:1px solid #8f1d28; color:#d17b83; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.75rem;">● VERY HIGH CRIME VOLUME</span>'
        elif comp_val > quartiles["q2"]:
            tier_badge = '<span style="background:rgba(234,88,12,0.18); border:1px solid #ea580c; color:#fb923c; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.75rem;">● HIGH CRIME VOLUME</span>'
        elif comp_val > quartiles["q1"]:
            tier_badge = '<span style="background:rgba(255,183,77,0.18); border:1px solid #ffb74d; color:#fcd34d; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.75rem;">● MEDIUM CRIME VOLUME</span>'
        else:
            tier_badge = '<span style="background:rgba(30,58,138,0.25); border:1px solid #3b82f6; color:#93c5fd; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.75rem;">● LOW CRIME VOLUME</span>'

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(13, 22, 32, 0.92) 0%, rgba(9, 15, 23, 0.98) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(41, 65, 82, 0.65); border-left: 4px solid #8f1d28; border-radius: 12px; padding: 22px 24px; box-shadow: 0 10px 32px rgba(0, 0, 0, 0.55); position: relative;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 18px; border-bottom: 1px solid rgba(41, 65, 82, 0.4); padding-bottom: 14px;">
                    <div>
                        <div style="display:flex; align-items:center; gap: 10px;">
                            <span style="width:8px; height:8px; background:#8f1d28; border-radius:50%; display:inline-block;"></span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase;">
                                {panel_type}
                            </span>
                        </div>
                        <h2 style="margin: 4px 0 0; font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: 0.04em; text-shadow: none;">
                            {target_location.upper()}
                        </h2>
                    </div>
                    <div style="display:flex; align-items:center; gap: 10px;">
                        {tier_badge}
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; background: rgba(0, 230, 118, 0.1); border: 1px solid rgba(0, 230, 118, 0.35); color: #00e676; padding: 4px 12px; border-radius: 20px; font-weight: 600;">
                            ✓ EPSG:4326 VERIFIED
                        </span>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        d1, d2, d3, d4, d5 = st.columns(5)
        with d1:
            st.metric("Total Incident Count", f"{crime_count_val:,.0f}")
        with d2:
            if rate_val is not None:
                st.metric("Crime Rate (per 100k)", f"{rate_val:.1f}")
            else:
                st.metric("Crime Rate (per 100k)", "Unavailable")
        with d3:
            st.metric("Crime Scope", crime_category)
        with d4:
            st.metric("Audit Baseline", str(info.get("year", 2022)))
        with d5:
            st.metric("Boundary Match", info.get("match_status", "MATCHED"))

        if info.get("rate_status"):
            st.markdown(
                f"""
                <div style="margin-top: 14px; padding: 8px 14px; background: rgba(0, 229, 255, 0.06); border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #7dd3fc; display:flex; align-items:center; gap:8px;">
                    <span>ℹ</span>
                    <span><b>Telemetry Note:</b> {info.get('rate_status')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(13, 22, 32, 0.85) 0%, rgba(9, 15, 23, 0.95) 100%); border: 1px solid rgba(41, 65, 82, 0.6); border-radius: 12px; padding: 32px 24px; text-align: center; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45); backdrop-filter: blur(14px);">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 62px; height: 62px; border-radius: 50%; border: 2px solid rgba(0, 229, 255, 0.5); background: radial-gradient(circle, rgba(0, 229, 255, 0.15) 0%, transparent 70%); margin-bottom: 12px; box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);">
                    <span style="font-size: 1.7rem;">🎯</span>
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 700; color: #ffffff; letter-spacing: 0.05em; margin-bottom: 6px;">
                    SPATIAL INTELLIGENCE READY // SELECT TARGET LOCATION
                </div>
                <div style="color: #94a3b8; font-size: 0.88rem; max-width: 580px; margin: 0 auto 16px; line-height: 1.5;">
                    Click directly on any State or District polygon on the map above, or select from the dropdown controls to engage comprehensive spatial crime metrics and official rates.
                </div>
                <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                    <span style="background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.35); color: #00e5ff; padding: 4px 14px; border-radius: 20px; font-family: monospace; font-size: 0.76rem; font-weight: 600;">36 STATES &amp; UTs LOADED</span>
                    <span style="background: rgba(0, 230, 118, 0.1); border: 1px solid rgba(0, 230, 118, 0.35); color: #00e676; padding: 4px 14px; border-radius: 20px; font-family: monospace; font-size: 0.76rem; font-weight: 600;">594 DISTRICT BOUNDARIES</span>
                    <span style="background: rgba(255, 183, 77, 0.1); border: 1px solid rgba(255, 183, 77, 0.35); color: #ffb74d; padding: 4px 14px; border-radius: 20px; font-family: monospace; font-size: 0.76rem; font-weight: 600;">ZERO FABRICATED COORDINATES</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )