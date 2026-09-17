# CRIME X — India-Focused Police Crime Intelligence & Analytics System

**CRIME X** is an academic police command-center intelligence and decision-support application built for exploring, analyzing, and mapping crime data across the Republic of India.

---

## 1. What CRIME X Is
CRIME X is a unified, multi-module intelligence system designed for law enforcement analysts, researchers, and academic evaluators. It integrates verified historical data from the National Crime Records Bureau (NCRB), authentic administrative GIS boundary mapping, machine learning risk estimation, experimental computer-vision fire hazard detection, operational case and alert management, and a grounded deterministic AI assistant.

---

## 2. Major Modules (10 Command-Center Views)
1. **Operations Dashboard**: High-level KPIs, national crime totals, cybercrime aggregates, GIS coverage metrics, system health, and active alerts overview.
2. **Crime Intelligence**: Deep-dive exploratory physical crime analytics, state rankings, district rankings, and category distributions.
3. **Geographic Crime Intelligence (Crime Map)**: Interactive Folium-powered choropleth maps displaying 36 Indian States and verified district administrative boundaries with dynamic quartile legends and location detail cards.
4. **Crime Prediction**: Supervised machine-learning regression for annual crime count estimation with explicit academic decision-support disclaimers.
5. **Cybercrime Intelligence**: Dedicated analytics covering IT Act offences, online financial fraud, identity theft, and cyber blackmailing.
6. **AI Fire Detection**: Computer-vision safety prototype powered by custom YOLO11n object detection for visual fire hazard identification.
7. **Cases & Investigation**: End-to-end investigation lifecycle management (Create, View, Update status, Close, Delete) with timeline events and evidence tracking.
8. **Alert Center**: Operational dispatch, severity triage (`INFO`, `WARNING`, `HIGH`, `CRITICAL`), read status tracking, and resolution lifecycle (`UNREAD` → `READ` → `RESOLVED`).
9. **AI Assistant**: Deterministic, grounded intelligence chatbot answering structured queries in English and Hinglish without hallucinating.
10. **System Settings**: Runtime health diagnostics, model status monitors, and SQLite datastore connection verification.

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)                  │
│  Dark Police Command Center Theme (src/ui/components.py) │
└────────────────────────────┬─────────────────────────────┘
                             │
     ┌───────────────────────┼────────────────────────┐
     ▼                       ▼                        ▼
┌──────────────┐    ┌─────────────────┐      ┌─────────────────┐
│ Service Layer│    │  GIS Pipeline   │      │ AI / ML Engine  │
│(src/services)│    │   (src/gis/)    │      │ (src/ml, src/dl)│
└──────┬───────┘    └────────┬────────┘      └────────┬────────┘
       │                     │                        │
       └──────────────┬──────┴────────────────────────┘
                      ▼
       ┌─────────────────────────────┐
       │ SQLAlchemy Repository Layer │
       │   (src/database/repository) │
       └──────────────┬──────────────┘
                      ▼
       ┌─────────────────────────────┐
       │       SQLite Database       │
       │ (database/crime_x.sqlite3)  │
       └─────────────────────────────┘
```

---

## 4. Data Sources & Provenance
- **Physical IPC Crime**: National Crime Records Bureau (*Crime in India 2022*), District Table 1.1 (934 district-level records covering 36 States/UTs).
- **Cybercrime & Fraud**: NCRB 2022 District Table 1.9 (covering IT Act violations and cyber financial fraud).
- **State Population & Crime Rates**: NCRB 2022 Table 1A.1 (*Mid-Year Projected Population in Lakhs* and official *Rate of Cognizable Crimes per 100k*).
- **Gujarat Historical Series**: Ahmedabad police jurisdiction historical series (2014–2018).
- **Temporal Baseline Disclaimer**: All crime data represents **historical NCRB baseline snapshots**, not live or real-time crime feeds.

---

## 5. India-Focused Scope
CRIME X is strictly tailored to the administrative geography, legal statutes (Indian Penal Code and Information Technology Act), and reporting structures of the Republic of India. No foreign, synthetic, or global datasets are utilized.

---

## 6. SQLite Database
- **Engine**: SQLite 3 accessed via SQLAlchemy 2.0 ORM (`database/crime_x.sqlite3`).
- **Normalized Schema**:
  - `states` & `districts`: Hierarchical administrative tables with unique constraints.
  - `crime_records`: Idempotent physical crime records with source provenance.
  - `cybercrime_records`: IT Act and cyber fraud category metrics.
  - `crime_predictions`: Persisted prediction history, input feature snapshots, and warnings.
  - `fire_detections`: Image inference audit logs, bounding boxes, and dimensions.
  - `investigations`, `investigation_events`, `evidence`: Full case lifecycle and audit trail.
  - `alerts`: Operational alert records with severity and resolution state.

---

## 7. Real GIS Implementation
- **State Boundaries**: Authentic GeoJSON boundary covering 36 States and Union Territories (including Ladakh, Jammu & Kashmir, and Telangana) sourced from DataMeet Open Maps.
- **District Boundaries**: Authentic GADM administrative district boundaries covering 594 features.
- **Name Normalization (`src/gis/name_normalizer.py`)**: 100% of States/UTs (36/36) matched. Over 400 district records matched cleanly with parent-state verification.
- **Zero Coordinate Fabrication**: No coordinates, centroids, or polygons are synthetically generated.
- **Conservative Matching Audit**: Unmatched non-geographic or specialized police entries (e.g. Railway Police divisions, commissionerate splits) are logged in `data/processed/gis_name_matching.csv` and transparently surfaced in UI diagnostics.

---

## 8. Machine Learning Limitations
- **Model**: Linear / Ridge Regression decision-support baseline trained on 3 historical observation years (2020–2022).
- **Academic Scope**: Strictly intended for exploratory decision support and trend comparison; it is **not** a guarantee of future crime occurrences.
- **Confidence Intervals**: Confidence intervals are explicitly marked **unavailable** because a 3-year time series cannot support statistically valid parametric confidence intervals.

---

## 9. Deep Learning (Vision) Limitations
- **Model**: Custom YOLO11n object detector (`models/dl/crime_x_fire_detector_v2.pt`).
- **Fire-Only Scope**: Trained on visual fire-only annotations. It does **not** detect smoke.
- **Not Safety Equipment**: Designated as an experimental academic computer-vision prototype for situational awareness; it is **not** certified fire protection equipment.

---

## 10. AI Assistant Behavior
- **Architecture**: Deterministic, bounded keyword routing engine (`src/services/ai_service.py`).
- **Grounding**: Queries are resolved strictly against SQLite, NCRB aggregations, GIS boundary data, and case records.
- **Non-Fabrication**: For unsupported, hypothetical, or ungrounded questions, the assistant returns a transparent notice: *"Data is not available in the current CRIME X database."*
- **Language Support**: Handles inquiries in English and practical Hinglish (e.g., *"India me sabse zyada crime kis state me hai?"*, *"Cyber fraud kaunsa highest hai?"*, *"Kitne investigation open hain?"*).

---

## 11. Installation
CRIME X runs directly in the existing Python environment (Python 3.11+ / Python 3.13):

```bash
# Install required dependencies
pip install -r requirements.txt
```

---

## 12. Running the Application
To launch the CRIME X police command center:

```bash
python -m streamlit run app.py
```

Open your browser at: **`http://localhost:8501`**

---

## 13. Running Automated Tests
CRIME X includes a comprehensive regression test suite covering all data layers, database operations, GIS pipelines, services, and ML/DL models:

```bash
python -m pytest -q
```

---

## 14. Known Limitations
1. **Historical Baseline**: Crime data represents the 2022 NCRB annual reporting cycle. It does not reflect live or current incidents.
2. **District Crime Rates**: District population figures are not provided in the standard NCRB district snapshot; district maps display actual crime counts, and rates are clearly marked as unavailable.
3. **Police vs Administrative Boundaries**: Certain specialized police jurisdictions (e.g., Railway Police, Commissionerate divisions) lack discrete administrative boundary polygons and appear in the diagnostic unmatched counts.
4. **TTS Interface**: Text-to-speech is configured as an optional/unconfigured interface in local environments without dedicated audio drivers.
#
