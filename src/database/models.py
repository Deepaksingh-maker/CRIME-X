"""Normalized SQLAlchemy models for persistent CRIME X data."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    districts: Mapped[list[District]] = relationship(back_populates="state", cascade="all, delete-orphan")


class District(Base):
    __tablename__ = "districts"
    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    state: Mapped[State] = relationship(back_populates="districts")
    __table_args__ = (UniqueConstraint("state_id", "name", name="uq_district_state_name"), Index("ix_district_state", "state_id"))


class CrimeRecord(Base):
    __tablename__ = "crime_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"))
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    crime_type: Mapped[str] = mapped_column(String(180), nullable=False)
    crime_count: Mapped[float] = mapped_column(Float, nullable=False)
    crime_rate: Mapped[float | None] = mapped_column(Float)
    source_dataset: Mapped[str] = mapped_column(String(240), nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, nullable=False)
    granularity: Mapped[str] = mapped_column(String(40), nullable=False)
    metrics: Mapped[dict | None] = mapped_column(JSON)
    __table_args__ = (Index("ix_crime_state_year", "state_id", "year"), Index("ix_crime_district_year", "district_id", "year"), Index("ix_crime_type", "crime_type"), Index("ix_crime_source", "source_dataset"), UniqueConstraint("state_id", "district_id", "year", "crime_type", "source_dataset", name="uq_crime_record"))


class CybercrimeRecord(Base):
    __tablename__ = "cybercrime_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"))
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    crime_type: Mapped[str] = mapped_column(String(180), nullable=False)
    crime_count: Mapped[float] = mapped_column(Float, nullable=False)
    source_dataset: Mapped[str] = mapped_column(String(240), nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[dict | None] = mapped_column(JSON)
    __table_args__ = (Index("ix_cyber_state_year", "state_id", "year"), Index("ix_cyber_district_year", "district_id", "year"), Index("ix_cyber_type", "crime_type"), Index("ix_cyber_source", "source_dataset"), UniqueConstraint("state_id", "district_id", "year", "crime_type", "source_dataset", name="uq_cyber_record"))


class CrimePrediction(Base):
    __tablename__ = "crime_predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"))
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    predicted_count: Mapped[float] = mapped_column(Float, nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    warning: Mapped[str | None] = mapped_column(Text)
    input_features: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class FireDetection(Base):
    __tablename__ = "fire_detections"
    id: Mapped[int] = mapped_column(primary_key=True)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    detections: Mapped[list | dict] = mapped_column(JSON, nullable=False)
    image_width: Mapped[int] = mapped_column(Integer, nullable=False)
    image_height: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Investigation(Base):
    __tablename__ = "investigations"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_reference: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="OPEN", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    case_type: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(240))
    assigned_officer: Mapped[str | None] = mapped_column(String(160))
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"))
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_investigation_id: Mapped[int | None] = mapped_column(ForeignKey("investigations.id"))
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="UNREAD", nullable=False)
    source: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class InvestigationEvent(Base):
    __tablename__ = "investigation_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_investigation_event_case", "investigation_id", "created_at"),)


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    file_reference: Mapped[str | None] = mapped_column(String(500))
    added_by: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)