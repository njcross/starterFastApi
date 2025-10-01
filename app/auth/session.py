import os
import functools
from datetime import timedelta
from flask import current_app, request, jsonify, g

def _session_ttl_seconds() -> int:
    days = int(os.getenv("SESSION_TTL_DAYS", "30"))
    return int(os.getenv("SESSION_TTL_SECONDS", str(days * 24 * 60 * 60)))

def create_session(user_id: int) -> str:
    import secrets
    sid = secrets.token_urlsafe(24)
    current_app.redis.setex(f"sess:{sid}", _session_ttl_seconds(), str(user_id))
    return sid

def get_current_user_id() -> int | None:
    sid = request.cookies.get("sid")
    if not sid:
        return None
    val = current_app.redis.get(f"sess:{sid}")
    return int(val) if val else None

def destroy_session(sid: str) -> None:
    """Remove session from Redis if it exists."""
    if sid:
        current_app.redis.delete(f"sess:{sid}")

def login_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        uid = get_current_user_id()
        if not uid:
            return jsonify({"error": "unauthorized"}), 401
        g.user_id = uid
        return fn(*args, **kwargs)
    return wrapper
