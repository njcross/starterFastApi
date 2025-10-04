# app/auth/deps.py
from fastapi import Depends, HTTPException, Request
from redis import Redis
from app.core.redis_client import get_redis 
from app.auth.session import get_current_user_id


def current_user_id(req: Request, r: Redis = Depends(get_redis)) -> int:
    sid = req.cookies.get("sid")
    uid = get_current_user_id(r, sid)

    if not uid:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return uid
