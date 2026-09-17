"""Import processed CRIME X records into the configured database."""

from src.database.connection import create_db_engine, get_session_factory
from src.database.repository import Repository
from src.database.schema import create_schema
from src.database.seed import seed_processed_data


if __name__ == "__main__":
    engine = create_db_engine()
    create_schema(engine)
    session = get_session_factory()()
    try:
        counts = seed_processed_data(Repository(session))
        print(counts)
    finally:
        session.close()