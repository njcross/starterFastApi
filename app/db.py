# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.config import settings

# Engine (works with psycopg/psycopg2/sqlite URLs)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Optional FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
