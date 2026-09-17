"""Environment-driven SQLAlchemy engine and session helpers."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL


def get_database_url() -> str:
    """Return the configured local SQLite URL."""

    return DATABASE_URL


def create_db_engine(database_url: str | None = None):
    """Create an SQLAlchemy engine without opening a connection eagerly."""

    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)


def get_session_factory(database_url: str | None = None):
    """Return a session factory for the configured or test database."""

    return sessionmaker(bind=create_db_engine(database_url), autoflush=False, expire_on_commit=False)


def check_connection(database_url: str | None = None) -> bool:
    """Perform an explicit connectivity check."""

    with create_db_engine(database_url).connect() as connection:
        connection.execute(text("SELECT 1"))
    return True