"""GIS Crime Intelligence Service for map data aggregation, choropleth generation, and spatial metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import folium
import numpy as np
import pandas as pd

from src.gis.geo_loader import (
    get_available_geojson_districts,
    get_available_geojson_states,
    get_district_geojson_for_state,
    get_states_geojson,
)
from src.gis.name_normalizer import match_district, match_state

PHYSICAL_CSV_PATH = Path("data/processed/physical_crime_2022_clean.csv")
CYBER_CSV_PATH = Path("data/processed/cybercrime_2022_clean.csv")
NCRB_TABLE_1A_PATH = Path("data/ncrb 2022/data/NCRB_Table_1A.1.csv")

# Color scale palette for choropleth (Low -> Very High)
QUARTILE_COLORS = {
    "Low": "#1e3a8a",        # Deep slate blue
    "Medium": "#d97706",     # Muted amber
    "High": "#ea580c",       # Alert orange
    "Very High": "#991b1b",   # Police crimson / blood red
    "No Data": "#334155",    # Slate gray
}

PHYSICAL_CATEGORIES = {
    "Total IPC Crimes": "total_cognizable_ipc_crimes_col_144",
    "Murder": "offences_affecting_the_human_body_murder_sec_302_ipc_col_3",
    "Kidnapping & Abduction": "offences_affecting_the_human_body_kidnapping_and_abduction_kidnapping_and_abduction_total_col_46_col_49_to_col_55_col_45",
    "Assault on Women": "offences_affecting_the_human_body_assault_on_women_with_intent_to_outrage_her_modesty_assault_on_women_with_intent_to_outrage_her_modesty_sec_354_ipc_total_col_36_col_37_col42_to_44_col_35",
    "Theft": "offences_against_property_theft_section_379_ipc_theft_total_col_92_col_93_col_91",
    "Burglary": "offences_against_property_burglary_sec_454_to_460_r_w_sec_380_ipc_burglary_total_col_95_col_96_col_94",
    "Robbery": "offences_against_property_robbery_sec_392_394_397_ipc_col_98",
    "Cheating & Forgery": "offences_relating_to_documents_property_marks_forgery_cheating_fraud_forgery_cheating_fraud_total_col_114_col_119_col_120_col_113",
}

CYBER_CATEGORIES = {
    "Total Cybercrimes": "total_cyber_crimes_a_b_c_col_51",
    "Identity Theft": "a_offences_under_i_t_act_computer_related_offences_identity_theft_sec_66c_col_9",
    "Cyber Blackmailing / Threat": "d_offences_under_ipc_cyber_blackmailing_threatening_col_38",
    "Fake News / Rumours": "d_offences_under_ipc_circulate_fake_false_news_rumours_sec_505_r_w_it_act_col_41",
    "Tampering Source Documents": "a_offences_under_i_t_act_tampering_computer_source_documents_sec_65_col_3",
}


class CrimeMapService:
    """Encapsulates GIS aggregation, rate computation, and Folium map generation."""

    def __init__(self) -> None:
        self._load_reference_data()

    def _load_reference_data(self) -> None:
        """Load static datasets used for spatial joins and official rates."""
        self.state_meta: dict[str, dict[str, Any]] = {}
        if NCRB_TABLE_1A_PATH.is_file():
            df_pop = pd.read_csv(NCRB_TABLE_1A_PATH)
            # Filter non-aggregate rows
            df_pop = df_pop[~df_pop["State/UT"].astype(str).str.lower().str.contains("total", na=False)]
            for _, row in df_pop.iterrows():
                st_name = str(row["State/UT"]).strip()
                try:
                    pop_lakhs = float(row.get("Mid-Year Projected Population (in Lakhs) (2022)", 0) or 0)
                except (ValueError, TypeError):
                    pop_lakhs = 0.0
                try:
                    rate_2022 = float(row.get("Rate of Cognizable Crimes (IPC) (2022)", 0) or 0)
                except (ValueError, TypeError):
                    rate_2022 = 0.0

                self.state_meta[st_name] = {
                    "population_lakhs": pop_lakhs,
                    "population_persons": pop_lakhs * 100000.0,
                    "official_rate_2022": rate_2022,
                }

    def get_filter_options(self, mode: str = "Physical Crime", selected_state: str | None = None) -> dict[str, Any]:
        """Return available dynamic filter options for UI controls."""
        years = [2022]
        year_note = "Only 2022 data is available for this detailed geographic dataset."

        if mode == "Cybercrime":
            categories = list(CYBER_CATEGORIES.keys())
        else:
            categories = list(PHYSICAL_CATEGORIES.keys())

        # Available states from GeoJSON
        states = ["All States"] + get_available_geojson_states()

        districts = ["All Districts"]
        if selected_state and selected_state != "All States":
            geo_districts = get_available_geojson_districts(selected_state)
            if geo_districts:
                districts += geo_districts

        metrics = ["Crime Count", "Crime Rate"]

        return {
            "modes": ["Physical Crime", "Cybercrime"],
            "years": years,
            "year_note": year_note,
            "categories": categories,
            "states": states,
            "districts": districts,
            "metrics": metrics,
        }

    def aggregate_crime_data(
        self,
        mode: str = "Physical Crime",
        level: str = "state",
        year: int = 2022,
        crime_category: str = "Total IPC Crimes",
        selected_state: str | None = None,
    ) -> pd.DataFrame:
        """Aggregate crime counts and compute rates joined with GeoJSON boundaries."""
        if mode == "Cybercrime":
            csv_path = CYBER_CSV_PATH
            category_col = CYBER_CATEGORIES.get(crime_category, "total_cyber_crimes_a_b_c_col_51")
        else:
            csv_path = PHYSICAL_CSV_PATH
            category_col = PHYSICAL_CATEGORIES.get(crime_category, "total_cognizable_ipc_crimes_col_144")

        if not csv_path.is_file():
            raise FileNotFoundError(f"Processed dataset '{csv_path}' not found.")

        df = pd.read_csv(csv_path)
        # Exclude aggregate rows
        df = df[~df["district"].astype(str).str.lower().str.contains("total", na=False)]
        df = df[~df["state_ut"].astype(str).str.lower().str.contains("total", na=False)]

        if category_col not in df.columns:
            # Fallback if specific subcategory not in dataset
            category_col = df.columns[-1]

        df[category_col] = pd.to_numeric(df[category_col], errors="coerce").fillna(0.0)

        rows: list[dict[str, Any]] = []

        if level == "state":
            geo_states = get_available_geojson_states()
            grouped = df.groupby("state_ut", as_index=False)[category_col].sum()

            for _, r in grouped.iterrows():
                raw_state = str(r["state_ut"])
                count = float(r[category_col])
                matched_geo, status, conf, reason = match_state(raw_state, geo_states)

                # Rate computation
                pop_info = self.state_meta.get(raw_state, {})
                pop_persons = pop_info.get("population_persons", 0.0)
                official_rate = pop_info.get("official_rate_2022")

                if mode == "Physical Crime" and crime_category == "Total IPC Crimes" and official_rate is not None and official_rate > 0:
                    rate = official_rate
                    rate_status = "Official NCRB Rate per 100k"
                elif pop_persons > 0:
                    rate = round((count / pop_persons) * 100000.0, 1)
                    rate_status = f"Calculated per 100,000 (Mid-year 2022 Pop: {pop_info.get('population_lakhs'):.1f} Lakhs)"
                else:
                    rate = None
                    rate_status = "Crime rate unavailable for selected data."

                rows.append({
                    "source_name": raw_state,
                    "geojson_name": matched_geo if status == "MATCHED" else None,
                    "state": raw_state,
                    "district": None,
                    "crime_count": count,
                    "crime_rate": rate,
                    "rate_status": rate_status,
                    "match_status": status,
                    "source": "NCRB 2022 (Historical Data)",
                    "year": year,
                    "crime_type": crime_category,
                })

        else:
            # District level aggregation
            if not selected_state or selected_state == "All States":
                subset = df.copy()
            else:
                subset = df[df["state_ut"].str.lower() == selected_state.lower()].copy()

            # District boundaries for selected state
            state_districts_geojson = get_district_geojson_for_state(selected_state or "India")
            geo_districts = [
                {"state": f["properties"].get("NAME_1", ""), "district": f["properties"].get("NAME_2", "")}
                for f in state_districts_geojson.get("features", [])
            ]

            grouped = subset.groupby(["state_ut", "district"], as_index=False)[category_col].sum()

            for _, r in grouped.iterrows():
                raw_state = str(r["state_ut"])
                raw_district = str(r["district"])
                count = float(r[category_col])

                matched_geo, status, conf, reason = match_district(raw_district, raw_state, geo_districts)

                rows.append({
                    "source_name": f"{raw_state} / {raw_district}",
                    "geojson_name": matched_geo if status == "MATCHED" else None,
                    "state": raw_state,
                    "district": raw_district,
                    "crime_count": count,
                    "crime_rate": None,  # District populations are not reported in NCRB snapshot
                    "rate_status": "Crime rate unavailable for selected data (district population not reported in NCRB snapshot).",
                    "match_status": status,
                    "source": "NCRB 2022 (Historical Data)",
                    "year": year,
                    "crime_type": crime_category,
                })

        return pd.DataFrame(rows)

    def calculate_quartiles(self, series: pd.Series) -> dict[str, Any]:
        """Compute robust dynamic quartiles from actual non-null data series."""
        clean = series.dropna()
        if len(clean) == 0:
            return {"min": 0, "q1": 0, "q2": 0, "q3": 0, "max": 0, "thresholds": [0, 0, 0]}

        min_val = float(clean.min())
        max_val = float(clean.max())
        q1 = float(np.percentile(clean, 25))
        q2 = float(np.percentile(clean, 50))
        q3 = float(np.percentile(clean, 75))

        return {
            "min": min_val,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "max": max_val,
            "thresholds": [q1, q2, q3],
        }

    def get_color_for_value(self, val: float | None, quartiles: dict[str, Any]) -> str:
        """Assign color based on dynamic quartile thresholds."""
        if val is None or np.isnan(val):
            return QUARTILE_COLORS["No Data"]
        q1, q2, q3 = quartiles["q1"], quartiles["q2"], quartiles["q3"]

        if val <= q1:
            return QUARTILE_COLORS["Low"]
        elif val <= q2:
            return QUARTILE_COLORS["Medium"]
        elif val <= q3:
            return QUARTILE_COLORS["High"]
        else:
            return QUARTILE_COLORS["Very High"]

    def build_folium_map(
        self,
        data_df: pd.DataFrame,
        level: str = "state",
        metric: str = "Crime Count",
        selected_state: str | None = None,
        selected_district: str | None = None,
    ) -> tuple[folium.Map, dict[str, Any]]:
        """Construct Folium map with GeoJSON polygons styled by dynamic crime metrics."""
        # Determine value column
        val_col = "crime_rate" if metric == "Crime Rate" else "crime_count"

        # Check if values exist
        has_rates = data_df[val_col].notnull().any()
        effective_val_col = val_col if has_rates else "crime_count"

        quartiles = self.calculate_quartiles(data_df[effective_val_col])

        # Create mapping of geojson_name -> row dict
        lookup: dict[str, dict[str, Any]] = {}
        for _, row in data_df.iterrows():
            geo_name = row.get("geojson_name")
            if geo_name:
                lookup[str(geo_name).lower()] = row.to_dict()

        # Load GeoJSON
        if level == "state" or not selected_state or selected_state == "All States":
            geojson_data = get_states_geojson()
            geo_key = "ST_NM"
            center = [22.5937, 78.9629]
            zoom = 4
        else:
            geojson_data = get_district_geojson_for_state(selected_state)
            geo_key = "NAME_2"
            center = [22.5937, 78.9629]
            zoom = 6

        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains="abcd",
            control_scale=True,
            zoom_control=True,
        )

        def style_function(feature: dict[str, Any]) -> dict[str, Any]:
            props = feature.get("properties", {})
            name = props.get(geo_key, "")
            row = lookup.get(str(name).lower())
            if row:
                val = row.get(effective_val_col)
                color = self.get_color_for_value(val, quartiles)
                fill_opacity = 0.75
            else:
                color = QUARTILE_COLORS["No Data"]
                fill_opacity = 0.35

            return {
                "fillColor": color,
                "color": "#e2e8f0",
                "weight": 1.2,
                "fillOpacity": fill_opacity,
            }

        def highlight_function(feature: dict[str, Any]) -> dict[str, Any]:
            return {
                "fillColor": "#ef4444",
                "color": "#ffffff",
                "weight": 2.5,
                "fillOpacity": 0.9,
            }

        # Inject hover and popup attributes into feature properties
        for feat in geojson_data.get("features", []):
            props = feat.get("properties", {})
            name = props.get(geo_key, "Unknown")
            row = lookup.get(str(name).lower())
            if row:
                c_val = f"{row.get('crime_count', 0):,.0f}"
                r_val = f"{row.get('crime_rate'):.1f}" if row.get("crime_rate") is not None else "Unavailable"
                props["cx_display_name"] = name
                props["cx_crime_count"] = c_val
                props["cx_crime_rate"] = r_val
                props["cx_status"] = "VERIFIED BOUNDARY"
            else:
                props["cx_display_name"] = name
                props["cx_crime_count"] = "No Record"
                props["cx_crime_rate"] = "Unavailable"
                props["cx_status"] = "No data for selected filter"

        tooltip_fields = ["cx_display_name", "cx_crime_count", "cx_crime_rate", "cx_status"]
        tooltip_aliases = ["Location:", "Total Crime:", "Crime Rate:", "Status:"]

        folium.GeoJson(
            geojson_data,
            name="Crime Distribution",
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=tooltip_aliases,
                localize=True,
                style=(
                    "background: rgba(9, 15, 24, 0.95); "
                    "color: #edf3f4; "
                    "font-family: 'Outfit', -apple-system, sans-serif; "
                    "font-size: 13px; "
                    "font-weight: 500; "
                    "padding: 12px 16px; "
                    "border: 1px solid #8f1d28; "
                    "border-radius: 8px; "
                    "box-shadow: 0 8px 24px rgba(0,0,0,0.8); "
                    "line-height: 1.6;"
                ),
            ),
        ).add_to(m)

        return m, quartiles

    def get_location_intelligence(
        self,
        name: str,
        level: str = "state",
        mode: str = "Physical Crime",
        year: int = 2022,
        parent_state: str | None = None,
    ) -> dict[str, Any]:
        """Fetch ground-truth detailed statistics for a selected location."""
        data_df = self.aggregate_crime_data(mode=mode, level=level, year=year, selected_state=parent_state)

        # Match name
        if level == "state":
            matched = data_df[data_df["source_name"].str.lower() == name.lower()]
        else:
            matched = data_df[data_df["district"].astype(str).str.lower() == name.lower()]

        if matched.empty:
            # Check geojson_name match
            matched = data_df[data_df["geojson_name"].astype(str).str.lower() == name.lower()]

        if matched.empty:
            return {
                "name": name,
                "found": False,
                "message": "Geographic boundary unavailable for this location in current selection.",
                "source": "NCRB 2022 (Historical Data)",
            }

        row = matched.iloc[0].to_dict()
        return {
            "name": name,
            "found": True,
            "state": row.get("state"),
            "district": row.get("district"),
            "crime_count": row.get("crime_count", 0.0),
            "crime_rate": row.get("crime_rate"),
            "rate_status": row.get("rate_status"),
            "year": row.get("year", 2022),
            "crime_type": row.get("crime_type"),
            "source": "NCRB 2022 (Historical Data)",
            "data_scope": "State-level historical dataset" if level == "state" else "District-level historical dataset",
            "match_status": row.get("match_status"),
        }

    def get_diagnostics(self, data_df: pd.DataFrame) -> dict[str, int]:
        """Compute counts of matched vs unmatched spatial units."""
        matched = int((data_df["match_status"] == "MATCHED").sum())
        unmatched = int((data_df["match_status"] == "UNMATCHED").sum())
        total = len(data_df)
        return {"matched": matched, "unmatched": unmatched, "total": total}
