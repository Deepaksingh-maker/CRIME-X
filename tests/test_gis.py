"""Comprehensive tests for CRIME X GIS Crime Intelligence module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.gis.crime_map_service import CrimeMapService
from src.gis.geo_loader import (
    get_available_geojson_districts,
    get_available_geojson_states,
    get_district_geojson_for_state,
    load_districts_geojson,
    load_states_geojson,
)
from src.gis.geo_validator import INDIA_BOUNDS, validate_geojson
from src.gis.name_normalizer import match_district, match_state


@pytest.fixture(scope="module")
def map_service() -> CrimeMapService:
    return CrimeMapService()


# 1. GeoJSON loading
def test_geojson_loading():
    states_data = load_states_geojson()
    assert isinstance(states_data, dict)
    assert states_data["type"] == "FeatureCollection"
    assert len(states_data["features"]) == 36

    districts_data = load_districts_geojson()
    assert isinstance(districts_data, dict)
    assert districts_data["type"] == "FeatureCollection"
    assert len(districts_data["features"]) == 594


# 2. GeoJSON validity
def test_geojson_validity():
    states_data = load_states_geojson()
    st_val = validate_geojson(states_data, check_bounds=True)
    assert st_val["valid"] is True
    assert st_val["feature_count"] == 36
    assert "Polygon" in st_val["geometry_types"] or "MultiPolygon" in st_val["geometry_types"]

    districts_data = load_districts_geojson()
    dist_val = validate_geojson(districts_data, check_bounds=True)
    assert dist_val["valid"] is True
    assert dist_val["feature_count"] == 594


# 3. State matching
def test_state_matching():
    geo_states = get_available_geojson_states()
    assert len(geo_states) == 36

    # Test direct match
    match, status, conf, _ = match_state("Uttar Pradesh", geo_states)
    assert status == "MATCHED"
    assert match == "Uttar Pradesh"
    assert conf == 1.0

    # Test alias and punctuation/& match
    match, status, conf, _ = match_state("Andaman and Nicobar Islands", geo_states)
    assert status == "MATCHED"
    assert match == "Andaman & Nicobar"

    match, status, conf, _ = match_state("Jammu and Kashmir", geo_states)
    assert status == "MATCHED"
    assert match == "Jammu & Kashmir"


# 4. District matching if available
def test_district_matching_within_state():
    gj_gujarat = get_district_geojson_for_state("Gujarat")
    assert len(gj_gujarat["features"]) > 0

    dist_records = [
        {"state": f["properties"].get("NAME_1", ""), "district": f["properties"].get("NAME_2", "")}
        for f in gj_gujarat["features"]
    ]

    matched, status, conf, _ = match_district("Ahmedabad", "Gujarat", dist_records)
    assert status == "MATCHED"
    assert matched == "Ahmadabad" or matched == "Ahmedabad"

    matched_surat, status_surat, _, _ = match_district("Surat", "Gujarat", dist_records)
    assert status_surat == "MATCHED"
    assert matched_surat == "Surat"


# 5. Unmatched names
def test_unmatched_names_no_forcing():
    geo_states = get_available_geojson_states()
    match, status, conf, reason = match_state("FictionalState123", geo_states)
    assert status == "UNMATCHED"
    assert match is None

    gj_ap = get_district_geojson_for_state("Andhra Pradesh")
    dist_records = [
        {"state": f["properties"].get("NAME_1", ""), "district": f["properties"].get("NAME_2", "")}
        for f in gj_ap["features"]
    ]
    # Railway police units should not be forced into district boundaries
    match_rly, status_rly, _, _ = match_district("Guntakal Railway", "Andhra Pradesh", dist_records)
    assert status_rly == "UNMATCHED"
    assert match_rly is None


# 6. Crime aggregation
def test_crime_aggregation(map_service: CrimeMapService):
    df_state = map_service.aggregate_crime_data(mode="Physical Crime", level="state")
    assert isinstance(df_state, pd.DataFrame)
    assert len(df_state) == 36
    # Uttar Pradesh is historically the highest crime count state in NCRB 2022
    up_row = df_state[df_state["source_name"] == "Uttar Pradesh"]
    assert not up_row.empty
    assert up_row.iloc[0]["crime_count"] == 401787.0
    assert up_row.iloc[0]["match_status"] == "MATCHED"


# 7. Crime-rate calculation
def test_crime_rate_calculation(map_service: CrimeMapService):
    df_state = map_service.aggregate_crime_data(mode="Physical Crime", level="state", crime_category="Total IPC Crimes")
    up_row = df_state[df_state["source_name"] == "Uttar Pradesh"].iloc[0]
    # Official NCRB Rate for UP in 2022 is 171.6
    assert up_row["crime_rate"] == 171.6
    assert "Official NCRB Rate" in up_row["rate_status"]

    # District level rate should be None with clear explanation
    df_dist = map_service.aggregate_crime_data(mode="Physical Crime", level="district", selected_state="Gujarat")
    ahmedabad_row = df_dist[df_dist["district"].str.lower() == "ahmedabad"]
    if not ahmedabad_row.empty:
        assert ahmedabad_row.iloc[0]["crime_rate"] is None
        assert "unavailable" in ahmedabad_row.iloc[0]["rate_status"].lower()


# 8. Year filtering
def test_year_filtering(map_service: CrimeMapService):
    opts = map_service.get_filter_options()
    assert 2022 in opts["years"]
    assert "2022" in opts["year_note"]


# 9. State filtering
def test_state_filtering(map_service: CrimeMapService):
    df_dist = map_service.aggregate_crime_data(mode="Physical Crime", level="district", selected_state="Gujarat")
    assert not df_dist.empty
    assert all(df_dist["state"].str.lower() == "gujarat")


# 10. District filtering
def test_district_filtering(map_service: CrimeMapService):
    dist_geo = get_available_geojson_districts("Gujarat")
    assert len(dist_geo) > 0
    assert "Ahmadabad" in dist_geo or "Ahmedabad" in dist_geo or "Surat" in dist_geo


# 11. Empty result handling
def test_empty_result_handling(map_service: CrimeMapService):
    info = map_service.get_location_intelligence("NonExistentPlace999", level="state")
    assert info["found"] is False
    assert "unavailable" in info["message"].lower()


# 12. No fake coordinates
def test_no_fake_coordinates():
    states_data = load_states_geojson()
    for feat in states_data["features"]:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        assert coords is not None and len(coords) > 0
        # Check first point of first ring
        pt = coords[0][0] if geom["type"] == "Polygon" else coords[0][0][0]
        lon, lat = float(pt[0]), float(pt[1])
        # Must be within real Indian bounds, absolutely never (0,0) or fabricated
        assert INDIA_BOUNDS["min_lon"] <= lon <= INDIA_BOUNDS["max_lon"]
        assert INDIA_BOUNDS["min_lat"] <= lat <= INDIA_BOUNDS["max_lat"]


# 13. Data provenance
def test_data_provenance(map_service: CrimeMapService):
    df_state = map_service.aggregate_crime_data(mode="Physical Crime", level="state")
    assert all(df_state["source"] == "NCRB 2022 (Historical Data)")
    info = map_service.get_location_intelligence("Uttar Pradesh", level="state")
    assert "NCRB" in info["source"]
    assert "Historical" in info["source"]
