"""Schema creation helpers."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from .models import Base


def create_schema(engine: Engine) -> None:
    """Create all CRIME X tables and indexes if they do not exist."""

    Base.metadata.create_all(engine)
    _migrate_existing_tables(engine)


def _migrate_existing_tables(engine: Engine) -> None:
    """Add additive nullable/default columns to an existing local SQLite file."""

    additions = {
        "investigations": {
            "case_type": "VARCHAR(120)",
            "location": "VARCHAR(240)",
            "assigned_officer": "VARCHAR(160)",
        },
        "alerts": {"status": "VARCHAR(20) DEFAULT 'UNREAD'", "source": "VARCHAR(80)"},
    }
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in additions.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))


def drop_schema(engine: Engine) -> None:
    """Drop only tables owned by CRIME X; intended for isolated tests."""

    Base.metadata.drop_all(engine)