# app/core/redis_client.py
from __future__ import annotations

from typing import Optional
from functools import lru_cache
from redis import Redis
from .config import settings

# --- test override hook (what your test expects) ---
# tests can set this to a FakeRedis; if None, we build a client lazily.
redis_client: Optional[Redis] = None

@lru_cache(maxsize=1)
def _build_client() -> Redis:
    # construct from env once (cached)
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis() -> Redis:
    """
    FastAPI dependency. Returns the test override if provided, otherwise
    returns a cached client built from REDIS_URL.
    """
    if redis_client is not None:
        return redis_client
    return _build_client()

# (optional) small helper for tests / app startup
def set_redis_override(client: Optional[Redis]) -> None:
    """Set or clear the test/client override and clear cache when clearing."""
    global redis_client
    redis_client = client
    if client is None:
        _build_client.cache_clear()  # ensure next call rebuilds from env
