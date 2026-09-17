"""Repository operations for CRIME X application data."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Alert, CrimePrediction, CrimeRecord, CybercrimeRecord, District, Evidence, FireDetection, Investigation, InvestigationEvent, State


def _as_dict(entity) -> dict:
    """Serialize a SQLAlchemy row using mapped columns only."""

    return {column.name: getattr(entity, column.name) for column in entity.__table__.columns}


class Repository:
    """Application repository backed by an injected SQLAlchemy session."""

    def __init__(self, session: Session):
        self.session = session

    def _get_state(self, name: str | None) -> State | None:
        if not name:
            return None
        state = self.session.scalar(select(State).where(State.name == name))
        if state is None:
            state = State(name=name)
            self.session.add(state)
            self.session.flush()
        return state

    def _get_district(self, state: State | None, name: str | None) -> District | None:
        if state is None or not name:
            return None
        district = self.session.scalar(select(District).where(District.state_id == state.id, District.name == name))
        if district is None:
            district = District(state_id=state.id, name=name)
            self.session.add(district)
            self.session.flush()
        return district

    def _geography(self, record: Mapping) -> tuple[int | None, int | None]:
        state = self._get_state(record.get("state"))
        district = self._get_district(state, record.get("district"))
        return state.id if state else None, district.id if district else None

    def insert_crime_records(self, records: Iterable[Mapping]) -> int:
        """Insert physical-crime rows idempotently by their natural key."""

        inserted = 0
        for record in records:
            state_id, district_id = self._geography(record)
            values = {
                "state_id": state_id,
                "district_id": district_id,
                "year": int(record["year"]),
                "crime_type": str(record["crime_type"]),
                "crime_count": float(record["crime_count"]),
                "crime_rate": record.get("crime_rate"),
                "source_dataset": str(record["source_dataset"]),
                "source_year": int(record["source_year"]),
                "granularity": str(record.get("granularity", "unknown")),
                "metrics": record.get("metrics"),
            }
            exists = self.session.scalar(select(CrimeRecord).where(
                CrimeRecord.state_id == state_id,
                CrimeRecord.district_id == district_id,
                CrimeRecord.year == values["year"],
                CrimeRecord.crime_type == values["crime_type"],
                CrimeRecord.source_dataset == values["source_dataset"],
            ))
            if exists is None:
                self.session.add(CrimeRecord(**values))
                inserted += 1
        self.session.commit()
        return inserted

    def get_crime_records(self, state: str | None = None, district: str | None = None, crime_type: str | None = None) -> list[dict]:
        """Return physical-crime rows with optional geography filters."""

        query = select(CrimeRecord, State.name, District.name).outerjoin(State, CrimeRecord.state_id == State.id).outerjoin(District, CrimeRecord.district_id == District.id)
        if state:
            query = query.where(State.name == state)
        if district:
            query = query.where(District.name == district)
        if crime_type:
            query = query.where(CrimeRecord.crime_type == crime_type)
        return [{**_as_dict(row), "state": state_name, "district": district_name} for row, state_name, district_name in self.session.execute(query).all()]

    def get_state_crime(self, state: str) -> list[dict]:
        return self.get_crime_records(state=state)

    def get_district_crime(self, district: str) -> list[dict]:
        return self.get_crime_records(district=district)

    def insert_cybercrime_records(self, records: Iterable[Mapping]) -> int:
        """Insert cybercrime rows idempotently by their natural key."""

        inserted = 0
        for record in records:
            state_id, district_id = self._geography(record)
            values = {
                "state_id": state_id,
                "district_id": district_id,
                "year": int(record["year"]),
                "crime_type": str(record["crime_type"]),
                "crime_count": float(record["crime_count"]),
                "source_dataset": str(record["source_dataset"]),
                "source_year": int(record["source_year"]),
                "metrics": record.get("metrics"),
            }
            exists = self.session.scalar(select(CybercrimeRecord).where(
                CybercrimeRecord.state_id == state_id,
                CybercrimeRecord.district_id == district_id,
                CybercrimeRecord.year == values["year"],
                CybercrimeRecord.crime_type == values["crime_type"],
                CybercrimeRecord.source_dataset == values["source_dataset"],
            ))
            if exists is None:
                self.session.add(CybercrimeRecord(**values))
                inserted += 1
        self.session.commit()
        return inserted

    def get_cybercrime_records(self, state: str | None = None, district: str | None = None, crime_type: str | None = None) -> list[dict]:
        query = select(CybercrimeRecord, State.name, District.name).outerjoin(State, CybercrimeRecord.state_id == State.id).outerjoin(District, CybercrimeRecord.district_id == District.id)
        if state:
            query = query.where(State.name == state)
        if district:
            query = query.where(District.name == district)
        if crime_type:
            query = query.where(CybercrimeRecord.crime_type == crime_type)
        return [{**_as_dict(row), "state": state_name, "district": district_name} for row, state_name, district_name in self.session.execute(query).all()]

    def get_fraud_records(self) -> list[dict]:
        query = select(CybercrimeRecord).where(CybercrimeRecord.crime_type.ilike("%fraud%"))
        return [_as_dict(row) for row in self.session.scalars(query).all()]

    def save_prediction(self, values: Mapping) -> dict:
        row = CrimePrediction(
            state_id=self._geography(values)[0],
            district_id=self._geography(values)[1],
            predicted_count=float(values["predicted_count"]),
            model=str(values["model"]),
            confidence=values.get("confidence"),
            warning=values.get("warning"),
            input_features=values.get("input_features"),
        )
        self.session.add(row)
        self.session.commit()
        return _as_dict(row)

    def get_prediction_history(self) -> list[dict]:
        return [_as_dict(row) for row in self.session.scalars(select(CrimePrediction).order_by(CrimePrediction.created_at.desc())).all()]

    def save_fire_detection(self, values: Mapping) -> dict:
        row = FireDetection(
            image_path=str(values["image_path"]),
            detections=values["detections"],
            image_width=int(values["image_width"]),
            image_height=int(values["image_height"]),
            model_name=str(values.get("model_name", "crime_x_fire_detector_v2.pt")),
        )
        self.session.add(row)
        self.session.commit()
        return _as_dict(row)

    def get_fire_detection_history(self) -> list[dict]:
        return [_as_dict(row) for row in self.session.scalars(select(FireDetection).order_by(FireDetection.created_at.desc())).all()]

    def create_investigation(self, values: Mapping) -> dict:
        row = Investigation(**{key: values[key] for key in ("case_reference", "title")}, status=values.get("status", "OPEN"), priority=values.get("priority", "MEDIUM"), case_type=values.get("case_type"), location=values.get("location"), assigned_officer=values.get("assigned_officer"), description=values.get("description"))
        state_id, district_id = self._geography(values)
        row.state_id, row.district_id = state_id, district_id
        self.session.add(row)
        self.session.commit()
        self.add_investigation_event(row.case_reference, "CASE_CREATED", row.title)
        return _as_dict(row)

    def update_investigation(self, case_reference: str, values: Mapping) -> dict:
        row = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if row is None:
            raise LookupError(f"Investigation not found: {case_reference}")
        for key in ("title", "status", "priority", "case_type", "location", "assigned_officer", "description"):
            if key in values:
                setattr(row, key, values[key])
        row.updated_at = datetime.utcnow()
        self.session.commit()
        self.add_investigation_event(case_reference, "CASE_UPDATED", ", ".join(values.keys()))
        return _as_dict(row)

    def get_investigation(self, case_reference: str) -> dict | None:
        row = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        return _as_dict(row) if row else None

    def delete_investigation(self, case_reference: str) -> bool:
        """Delete an investigation by case reference."""

        row = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True

    def list_investigations(self, status: str | None = None, priority: str | None = None, search: str | None = None) -> list[dict]:
        query = select(Investigation).order_by(Investigation.updated_at.desc())
        if status:
            query = query.where(Investigation.status == status)
        if priority:
            query = query.where(Investigation.priority == priority)
        rows = [_as_dict(row) for row in self.session.scalars(query).all()]
        if search:
            term = search.lower()
            rows = [row for row in rows if term in str(row).lower()]
        return rows

    def count_investigations(self, status: str | None = None) -> int:
        return len(self.list_investigations(status=status))

    def add_investigation_event(self, case_reference: str, event_type: str, details: str | None = None) -> dict:
        investigation = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if investigation is None:
            raise LookupError(f"Investigation not found: {case_reference}")
        row = InvestigationEvent(investigation_id=investigation.id, event_type=event_type, details=details)
        self.session.add(row)
        self.session.commit()
        return _as_dict(row)

    def get_investigation_timeline(self, case_reference: str) -> list[dict]:
        investigation = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if investigation is None:
            return []
        return [_as_dict(row) for row in self.session.scalars(select(InvestigationEvent).where(InvestigationEvent.investigation_id == investigation.id).order_by(InvestigationEvent.created_at)).all()]

    def add_evidence(self, case_reference: str, values: Mapping) -> dict:
        investigation = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if investigation is None:
            raise LookupError(f"Investigation not found: {case_reference}")
        row = Evidence(investigation_id=investigation.id, evidence_type=str(values["evidence_type"]), description=values.get("description"), file_reference=values.get("file_reference"), added_by=values.get("added_by"))
        self.session.add(row)
        self.session.commit()
        self.add_investigation_event(case_reference, "EVIDENCE_ADDED", row.evidence_type)
        return _as_dict(row)

    def get_evidence(self, case_reference: str) -> list[dict]:
        investigation = self.session.scalar(select(Investigation).where(Investigation.case_reference == case_reference))
        if investigation is None:
            return []
        return [_as_dict(row) for row in self.session.scalars(select(Evidence).where(Evidence.investigation_id == investigation.id).order_by(Evidence.created_at.desc())).all()]

    def create_alert(self, values: Mapping) -> dict:
        row = Alert(alert_type=str(values["alert_type"]), severity=str(values["severity"]), message=str(values["message"]), related_investigation_id=values.get("related_investigation_id"), is_read=bool(values.get("is_read", False)), status=str(values.get("status", "UNREAD")), source=values.get("source"))
        self.session.add(row)
        self.session.commit()
        return _as_dict(row)

    def get_alerts(self, unread_only: bool = False, status: str | None = None) -> list[dict]:
        query = select(Alert).order_by(Alert.created_at.desc())
        if unread_only:
            query = query.where(Alert.is_read.is_(False))
        if status:
            query = query.where(Alert.status == status)
        return [_as_dict(row) for row in self.session.scalars(query).all()]

    def mark_alert_read(self, alert_id: int) -> dict:
        row = self.session.get(Alert, alert_id)
        if row is None:
            raise LookupError(f"Alert not found: {alert_id}")
        row.is_read = True
        row.status = "READ"
        self.session.commit()
        return _as_dict(row)

    def resolve_alert(self, alert_id: int) -> dict:
        row = self.session.get(Alert, alert_id)
        if row is None:
            raise LookupError(f"Alert not found: {alert_id}")
        row.is_read = True
        row.status = "RESOLVED"
        self.session.commit()
        return _as_dict(row)

    def delete_alert(self, alert_id: int) -> bool:
        row = self.session.get(Alert, alert_id)
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True