"""Validation utilities for GeoJSON administrative boundaries."""

from __future__ import annotations

from typing import Any


# Bounding box constraints for the territory of India (with standard territorial buffer)
INDIA_BOUNDS = {
    "min_lon": 65.0,
    "max_lon": 100.0,
    "min_lat": 5.0,
    "max_lat": 40.0,
}


def _extract_coords(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    """Flatten polygon / multipolygon coordinates into list of (lon, lat) tuples."""
    coords: list[tuple[float, float]] = []
    g_type = geometry.get("type", "")
    raw = geometry.get("coordinates", [])

    if g_type == "Polygon":
        for ring in raw:
            for pt in ring:
                if len(pt) >= 2:
                    coords.append((float(pt[0]), float(pt[1])))
    elif g_type == "MultiPolygon":
        for poly in raw:
            for ring in poly:
                for pt in ring:
                    if len(pt) >= 2:
                        coords.append((float(pt[0]), float(pt[1])))
    return coords


def validate_geojson(data: dict[str, Any], check_bounds: bool = True) -> dict[str, Any]:
    """Validate that GeoJSON data conforms to standard FeatureCollection format and India bounds."""
    if not isinstance(data, dict):
        raise ValueError("GeoJSON must be a dictionary.")

    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Expected type 'FeatureCollection', got '{data.get('type')}'")

    features = data.get("features")
    if not isinstance(features, list) or len(features) == 0:
        raise ValueError("GeoJSON FeatureCollection contains no features.")

    geom_types = set()
    all_lons: list[float] = []
    all_lats: list[float] = []

    for idx, feature in enumerate(features):
        if not isinstance(feature, dict):
            raise ValueError(f"Feature at index {idx} is not an object.")
        if feature.get("type") != "Feature":
            raise ValueError(f"Feature at index {idx} has invalid type '{feature.get('type')}'.")

        geom = feature.get("geometry")
        if not geom or not isinstance(geom, dict):
            raise ValueError(f"Feature at index {idx} lacks a valid geometry object.")

        g_type = geom.get("type")
        if g_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"Feature at index {idx} has unsupported geometry type '{g_type}'.")
        geom_types.add(g_type)

        coords = _extract_coords(geom)
        if not coords:
            raise ValueError(f"Feature at index {idx} has empty coordinates.")

        for lon, lat in coords:
            all_lons.append(lon)
            all_lats.append(lat)

    min_lon, max_lon = min(all_lons), max(all_lons)
    min_lat, max_lat = min(all_lats), max(all_lats)

    if check_bounds:
        # Check if coordinates lie within Indian geographical territory
        if max_lat < INDIA_BOUNDS["min_lat"] or min_lat > INDIA_BOUNDS["max_lat"]:
            raise ValueError(f"Latitude range [{min_lat}, {max_lat}] outside valid Indian bounds.")
        if max_lon < INDIA_BOUNDS["min_lon"] or min_lon > INDIA_BOUNDS["max_lon"]:
            raise ValueError(f"Longitude range [{min_lon}, {max_lon}] outside valid Indian bounds.")

    return {
        "valid": True,
        "feature_count": len(features),
        "geometry_types": sorted(list(geom_types)),
        "bounds": {
            "min_lon": min_lon,
            "max_lon": max_lon,
            "min_lat": min_lat,
            "max_lat": max_lat,
        },
    }
