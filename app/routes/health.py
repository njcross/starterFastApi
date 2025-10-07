# app/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from redis import Redis

from ..db import engine
from ..core.redis_client import get_redis
from ..schemas.health import HealthResponse, RedisPingResponse, DBVersionResponse, ErrorResponse
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter(prefix="/api", tags=["Health"])
@router.get(
    "/health",
    summary="Liveness probe",
    response_model=HealthResponse,
    responses={
        200: {"model": HealthResponse, "description": "Service is alive"},
    },
)
def health() -> HealthResponse:
    return HealthResponse(ok=True)


@router.get(
    "/ping-redis",
    summary="Round-trip Redis",
    response_model=RedisPingResponse,
    responses={
        200: {"model": RedisPingResponse, "description": "Cached value returned"},
    },
)
def ping_redis(r: Redis = Depends(get_redis)) -> RedisPingResponse:
    r.set("hello", "world", ex=30)
    val = r.get("hello")
    # Safety if decode_responses=False
    if isinstance(val, bytes):
        val = val.decode("utf-8", errors="replace")
    return RedisPingResponse(redis=str(val))


@router.get(
    "/db-version",
    summary="Database version",
    responses={
        200: {"model": DBVersionResponse, "description": "Postgres version string"},
        500: {"model": ErrorResponse, "description": "Database not reachable / error"},
    },
)
def db_version():
    try:
        with engine.connect() as conn:
            row = conn.execute(text("select version()")).fetchone()
            return DBVersionResponse(postgres_version=row[0])
    except Exception as e:
        # Return a modeled 500 so docs match runtime shape
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error=str(e)).model_dump(),
        )
