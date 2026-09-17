"""Initialize the configured CRIME X database schema."""

from src.database.connection import create_db_engine
from src.database.schema import create_schema


if __name__ == "__main__":
    engine = create_db_engine()
    create_schema(engine)
    print("CRIME X database schema created.")