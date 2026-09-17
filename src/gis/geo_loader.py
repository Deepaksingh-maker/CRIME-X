"""High-performance cached GeoJSON loader with spatial indexing."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.gis.name_normalizer import canonical_key, match_state

DEFAULT_GEO_DIR = Path("data/geospatial")
STATES_GEOJSON_FILE = DEFAULT_GEO_DIR / "india_states.geojson"
DISTRICTS_GEOJSON_FILE = DEFAULT_GEO_DIR / "india_districts.geojson"


@lru_cache(maxsize=1)
def load_states_geojson(file_path: str = str(STATES_GEOJSON_FILE)) -> dict[str, Any]:
    """Load and cache the State/UT GeoJSON FeatureCollection."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"State GeoJSON file not found at '{path}'")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@lru_cache(maxsize=1)
def load_districts_geojson(file_path: str = str(DISTRICTS_GEOJSON_FILE)) -> dict[str, Any]:
    """Load and cache the full District GeoJSON FeatureCollection."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"District GeoJSON file not found at '{path}'")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@lru_cache(maxsize=1)
def get_districts_by_state_index(file_path: str = str(DISTRICTS_GEOJSON_FILE)) -> dict[str, list[dict[str, Any]]]:
    """Pre-index district features by normalized state name for fast retrieval."""
    full_data = load_districts_geojson(file_path)
    index: dict[str, list[dict[str, Any]]] = {}

    for feature in full_data.get("features", []):
        props = feature.get("properties", {})
        raw_state = props.get("NAME_1", "")
        norm_key = canonical_key(raw_state)
        if norm_key:
            if norm_key not in index:
                index[norm_key] = []
            index[norm_key].append(feature)

    return index


def get_states_geojson(file_path: str = str(STATES_GEOJSON_FILE)) -> dict[str, Any]:
    """Retrieve state-level GeoJSON FeatureCollection."""
    return load_states_geojson(file_path)


def get_district_geojson_for_state(state_name: str, file_path: str = str(DISTRICTS_GEOJSON_FILE)) -> dict[str, Any]:
    """Extract a lightweight GeoJSON FeatureCollection containing only districts for a selected state."""
    state_index = get_districts_by_state_index(file_path)
    states_data = load_states_geojson()
    available_geo_states = [feat["properties"]["ST_NM"] for feat in states_data.get("features", [])]

    # Resolve state name through normalizer
    matched_state, status, _, _ = match_state(state_name, available_geo_states)
    lookup_name = matched_state or state_name
    key = canonical_key(lookup_name)

    features = state_index.get(key, [])
    # Fallback to loose search if direct key not present
    if not features:
        for idx_key, feat_list in state_index.items():
            if key in idx_key or idx_key in key:
                features = feat_list
                break

    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }


def get_available_geojson_states(file_path: str = str(STATES_GEOJSON_FILE)) -> list[str]:
    """Return sorted list of all 36 state names from GeoJSON."""
    data = load_states_geojson(file_path)
    return sorted(feat["properties"]["ST_NM"] for feat in data.get("features", []))


def get_available_geojson_districts(state_name: str, file_path: str = str(DISTRICTS_GEOJSON_FILE)) -> list[str]:
    """Return sorted list of available district names within a state from GeoJSON."""
    fc = get_district_geojson_for_state(state_name, file_path)
    return sorted(list(set(feat["properties"].get("NAME_2", "") for feat in fc.get("features", []))))
