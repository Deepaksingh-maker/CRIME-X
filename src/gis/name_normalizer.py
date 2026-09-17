"""Name normalization and matching between NCRB crime records and GeoJSON boundaries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

import pandas as pd


# Explicit known standard aliases between NCRB conventions and GeoJSON official names
STATE_ALIASES: dict[str, str] = {
    "andaman and nicobar islands": "Andaman & Nicobar",
    "andaman & nicobar islands": "Andaman & Nicobar",
    "jammu and kashmir": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "the dadra and nagar haveli and daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "nct of delhi": "Delhi",
    "delhi ut": "Delhi",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
}


def canonical_key(text: str | None) -> str:
    """Normalize string for safe, punctuation-insensitive string matching."""
    if not text:
        return ""
    cleaned = str(text).strip().lower()
    cleaned = cleaned.replace("&", "and")
    # Remove boundary noise words like 'islands', 'district', 'state', 'ut'
    cleaned = re.sub(r"\b(islands|district|districts|state|ut|commissionerate|commissioner)\b", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9]", "", cleaned)
    return cleaned


def match_state(source_name: str, geojson_names: Sequence[str]) -> tuple[str | None, str, float, str]:
    """Match a source state name against GeoJSON state names deterministically."""
    if not source_name or not str(source_name).strip():
        return None, "UNMATCHED", 0.0, "Empty source name"

    clean_source = source_name.strip()
    lower_source = clean_source.lower()

    # 1. Direct exact match
    for geo in geojson_names:
        if clean_source.lower() == geo.lower():
            return geo, "MATCHED", 1.0, "Exact case-insensitive match"

    # 2. Known standard alias
    if lower_source in STATE_ALIASES:
        target = STATE_ALIASES[lower_source]
        for geo in geojson_names:
            if geo.lower() == target.lower():
                return geo, "MATCHED", 1.0, f"Standard alias: {target}"

    # 3. Canonical key match
    key_source = canonical_key(clean_source)
    candidates = [geo for geo in geojson_names if canonical_key(geo) == key_source]
    if len(candidates) == 1:
        return candidates[0], "MATCHED", 0.95, "Normalized punctuation/whitespace match"
    elif len(candidates) > 1:
        return None, "AMBIGUOUS", 0.5, f"Multiple candidates: {', '.join(candidates)}"

    return None, "UNMATCHED", 0.0, "No safe boundary match found"


# Standard verified district aliases between NCRB conventions and GeoJSON official names
DISTRICT_ALIASES: dict[str, str] = {
    "ahmedabad": "Ahmadabad",
    "ahmadabad": "Ahmadabad",
    "banaskantha": "Banas Kantha",
    "sabarkantha": "Sabar Kantha",
    "panchmahal": "Panch Mahals",
    "panchmahals": "Panch Mahals",
    "dang": "The Dangs",
    "dangs": "The Dangs",
    "the dang": "The Dangs",
    "mehsana": "Mahesana",
    "kutch": "Kachchh",
    "bengaluru": "Bangalore",
    "bengaluru urban": "Bangalore",
    "bangalore": "Bangalore",
    "prayagraj": "Allahabad",
    "allahabad": "Allahabad",
    "gurugram": "Gurgaon",
    "gurgaon": "Gurgaon",
    "visakhapatnam": "Vishakhapatnam",
    "vishakhapatnam": "Vishakhapatnam",
    "pondicherry": "Pondicherry",
    "puducherry": "Pondicherry",
}


def match_district(
    source_district: str,
    source_state: str,
    geojson_district_records: Sequence[dict[str, str]],
) -> tuple[str | None, str, float, str]:
    """Match district within its verified parent state.

    geojson_district_records expects a list of dicts with keys 'state' and 'district'.
    """
    if not source_district or not str(source_district).strip():
        return None, "UNMATCHED", 0.0, "Empty source district"

    clean_d = source_district.strip()
    clean_s = source_state.strip()
    norm_s = canonical_key(clean_s)

    # Filter district records that belong to the same state
    state_records = [
        rec["district"]
        for rec in geojson_district_records
        if canonical_key(rec.get("state")) == norm_s
    ]

    if not state_records:
        return None, "UNMATCHED", 0.0, f"Parent state '{source_state}' not found in district GIS data"

    # 1. Direct exact match in state
    for geo_d in state_records:
        if clean_d.lower() == geo_d.lower():
            return geo_d, "MATCHED", 1.0, "Exact match in parent state"

    # 2. Known standard alias
    lower_d = clean_d.lower()
    if lower_d in DISTRICT_ALIASES:
        target = DISTRICT_ALIASES[lower_d]
        for geo_d in state_records:
            if geo_d.lower() == target.lower():
                return geo_d, "MATCHED", 1.0, f"Standard alias: {target}"

    # 3. Canonical key match
    key_d = canonical_key(clean_d)
    candidates = [geo_d for geo_d in state_records if canonical_key(geo_d) == key_d]
    if len(candidates) == 1:
        return candidates[0], "MATCHED", 0.9, "Normalized district match in state"
    elif len(candidates) > 1:
        return None, "AMBIGUOUS", 0.4, f"Multiple candidates in state: {', '.join(candidates)}"

    # Special handling for police commissionerates / railways / newly partitioned districts
    if any(term in clean_d.lower() for term in ("railway", "rly", "commissionerate")):
        return None, "UNMATCHED", 0.0, "Specialized police jurisdiction without discrete GADM boundary"

    return None, "UNMATCHED", 0.0, "District boundary unavailable in GeoJSON"


def create_gis_matching_report(
    physical_csv_path: Path,
    states_geojson_path: Path,
    districts_geojson_path: Path,
    output_report_path: Path,
) -> pd.DataFrame:
    """Generate and write the comprehensive gis_name_matching.csv audit report."""
    import json

    with open(states_geojson_path, "r", encoding="utf-8") as f:
        st_data = json.load(f)
    geo_states = [feat["properties"]["ST_NM"] for feat in st_data["features"]]

    with open(districts_geojson_path, "r", encoding="utf-8") as f:
        d_data = json.load(f)
    geo_districts = [
        {"state": feat["properties"].get("NAME_1", ""), "district": feat["properties"].get("NAME_2", "")}
        for feat in d_data["features"]
    ]

    df = pd.read_csv(physical_csv_path)
    rows: list[dict] = []

    # 1. State matching audit
    ncrb_states = sorted(s for s in df["state_ut"].dropna().unique() if "total" not in str(s).lower())
    for st in ncrb_states:
        matched, status, conf, reason = match_state(st, geo_states)
        rows.append({
            "source_name": f"[STATE] {st}",
            "geojson_name": matched or "N/A",
            "match_status": status,
            "confidence": conf,
            "reason": reason,
        })

    # 2. District matching audit
    non_total_df = df[~df["district"].astype(str).str.lower().str.contains("total", na=False)]
    district_pairs = non_total_df[["state_ut", "district"]].drop_duplicates()

    for _, pair in district_pairs.iterrows():
        s_name = str(pair["state_ut"])
        d_name = str(pair["district"])
        matched, status, conf, reason = match_district(d_name, s_name, geo_districts)
        rows.append({
            "source_name": f"{s_name} / {d_name}",
            "geojson_name": matched or "N/A",
            "match_status": status,
            "confidence": conf,
            "reason": reason,
        })

    report_df = pd.DataFrame(rows)
    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(output_report_path, index=False)
    return report_df
