from sqlalchemy import inspect

from src.database.connection import check_connection, create_db_engine
from src.database.models import Base
from src.database.schema import create_schema


def test_sqlite_connection_and_schema_creation():
    engine = create_db_engine("sqlite:///:memory:")
    assert check_connection("sqlite:///:memory:") is True
    create_schema(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"states", "districts", "crime_records", "cybercrime_records", "crime_predictions", "fire_detections", "investigations", "alerts"} <= tables