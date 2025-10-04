# app/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from redis import Redis

from ..db import engine
from ..core.redis_client import get_redis

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health", summary="Liveness probe")
def health():
    return {"ok": True}

@router.get("/ping-redis", summary="Round-trip Redis")
def ping_redis(r: Redis = Depends(get_redis)):
    r.set("hello", "world", ex=30)
    return {"redis": r.get("hello")}

@router.get("/db-version", summary="Database version")
def db_version():
    try:
        with engine.connect() as conn:
            row = conn.execute(text("select version()")).fetchone()
            return {"postgres_version": row[0]}
    except Exception as e:
        # Keep it structured for clients
        return {"error": str(e)}
