from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SOFT_DELETE_TABLES = (
    "vehicles",
    "drivers",
    "contracts",
    "payments",
    "maintenances",
    "documents",
    "incidents",
)


def ensure_soft_delete_columns() -> None:
    """Add soft-delete columns to existing SQLite tables without dropping data.

    SQLAlchemy's create_all creates missing tables but does not migrate existing
    ones. This small compatibility migration keeps local/demo deployments safe
    while avoiding destructive changes.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_columns = {
        "deleted_at": "DATETIME",
        "deleted_by": "INTEGER",
        "delete_reason": "VARCHAR(255)",
    }

    with engine.begin() as conn:
        for table_name in SOFT_DELETE_TABLES:
            if table_name not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
