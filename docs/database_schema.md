# CRIME X Database Schema

## Connection

CRIME X uses a local SQLite database through SQLAlchemy. Set `DATABASE_URL` when a different SQLite file is needed. Tests use isolated in-memory SQLite databases.

## Tables

| Table | Purpose |
| --- | --- |
| `states` | Normalized state/UT names. |
| `districts` | District names scoped to a state. |
| `crime_records` | Physical crime and separate Gujarat city-series aggregates. |
| `cybercrime_records` | District cybercrime categories and fraud categories. |
| `crime_predictions` | Historical ML decision-support predictions and inputs. |
| `fire_detections` | Fire detector inference history and structured detections. |
| `investigations` | Application investigation records. |
| `alerts` | Alert messages and read state. |

`crime_records` and `cybercrime_records` retain `source_dataset`, `source_year`, and `granularity`. Their natural-key constraints prevent duplicate imports. The Gujarat city series is not merged with district NCRB data; it is stored with `granularity = city` and its city name in `metrics`.

## Relationships

- `states` has many `districts`.
- `crime_records` and `cybercrime_records` optionally reference normalized states and districts.
- `crime_predictions` optionally references a state/district context.
- `investigations` optionally reference a state/district context.
- `alerts` optionally reference an investigation.

## Indexes and constraints

Indexes cover state/year, district/year, crime type, and source dataset on both analytical record tables. State names are unique, district names are unique within a state, and analytical rows use a composite natural-key uniqueness constraint. Investigation case references are unique. Model files and image binaries remain outside the database.