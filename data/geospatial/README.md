# CRIME X - Geospatial Boundary Data Documentation

This directory contains authentic, verified administrative boundary GeoJSON datasets for the Republic of India. No coordinates, boundaries, or polygons are manually fabricated or randomly generated.

---

## 1. Indian States & Union Territories Boundary

- **Filename**: `india_states.geojson`
- **Administrative Level**: Admin 1 (States and Union Territories of India)
- **Feature Count**: 36 features (28 States, 8 Union Territories, including Ladakh, Jammu & Kashmir, and Telangana)
- **Properties Key**: `ST_NM` (State/UT Name)
- **Source Reference**: DataMeet Community Maps / Open Data Gist (`jbrobst/india_states.geojson`)
- **Source URL**: `https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson`
- **Coordinate Reference System (CRS)**: EPSG:4326 (WGS84 Latitude / Longitude)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Open Data
- **File Size**: ~1.02 MB

---

## 2. Indian Districts Boundary

- **Filename**: `india_districts.geojson`
- **Administrative Level**: Admin 2 (Districts of India)
- **Source Reference**: GADM / Geohacker India Spatial Repository
- **Source URL**: `https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson`
- **Properties Keys**:
  - `NAME_1`: State / UT Name
  - `NAME_2`: District Name
  - `ENGTYPE_2` / `TYPE_2`: "District"
- **Coordinate Reference System (CRS)**: EPSG:4326 (WGS84)
- **License**: Open Data / GADM Academic & Public Use License
- **File Size**: ~34.5 MB

---

## 3. Data Integrity & Verification Policy

1. **Zero Coordinate Fabrication**: No coordinates, vertices, centroids, or bounding boxes are synthetically invented.
2. **Deterministic Name Normalization**: Discrepancies between NCRB naming conventions and GeoJSON official boundary tags are resolved deterministically and tracked in `data/processed/gis_name_matching.csv`.
3. **No Unsafe Forced Matching**: If a district or administrative unit cannot be verified with certainty, it is flagged as `UNMATCHED` and reported in diagnostics rather than assigned a wrong polygon.
