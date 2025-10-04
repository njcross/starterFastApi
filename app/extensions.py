# app/extensions.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis import Redis
from .core.config import settings

# --- SQLAlchemy setup ---
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Redis setup ---
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
