from typing import Optional
from redis import Redis
import secrets
from ..core.redis_client import get_redis

def _session_ttl_seconds() -> int:
    return 60 * 60 * 24 * 7  # 7 days

def create_session(user_id: int, *, r: Redis | None = None) -> str:
    """Create a session for user_id and return sid."""
    r = r or get_redis
    sid = secrets.token_urlsafe(32)
    r.setex(f"sess:{sid}", _session_ttl_seconds(), str(user_id))
    return sid

def get_current_user_id(r: Redis, sid: Optional[str]) -> Optional[int]:
    """Return user id from sid, or None if not found/invalid."""
    if not sid:
        return None
    val = r.get(f"sess:{sid}")
    return int(val) if val is not None else None

def destroy_session(sid: str, r: Redis) -> None:
    r.delete(f"sess:{sid}")

# Optional: dependency factory for protected routes
from fastapi import Depends, HTTPException, Request
from app.core.redis_client import get_redis

def require_auth():
    def _dep(req: Request, r: Redis = Depends(get_redis)) -> int:
        uid = get_current_user_id(r, req.cookies.get("sid"))
        if not uid:
            raise HTTPException(status_code=401)
        return uid
    return _dep
