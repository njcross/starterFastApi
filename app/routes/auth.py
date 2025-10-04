from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from redis import Redis

from ..db import get_db
from ..models.user import User
from ..schemas.auth import EmailRequest
from ..core.redis_client import get_redis
from ..auth.session import create_session, destroy_session
from ..core.config import settings
from ..core.emailer import send_email   
from ..auth.deps import current_user_id
from os import getenv

router = APIRouter(prefix="/api/auth", tags=["Auth"])

from fastapi import BackgroundTasks

@router.post("/request-link", summary="Send magic login link")
def request_link(
    payload: EmailRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis),
):
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    import secrets
    token = secrets.token_urlsafe(32)
    r.setex(f"magic:{token}", settings.MAGIC_TOKEN_TTL, str(user.id))

    link = f"{settings.BACKEND_PUBLIC_URL}/api/auth/callback?token={token}"
    background.add_task(
        send_email,
        to_addr=email,
        subject="Your sign-in link",
        body=f"Click to sign in: {link}\n\nThis link expires in {settings.MAGIC_TOKEN_TTL // 60} minutes.",
    )
    return {"sent": True}

@router.get("/callback")
def callback(token: str, response: Response, r: Redis = Depends(get_redis)):
    user_id = r.get(f"magic:{token}")
    if not user_id:
        response.status_code = 400
        return {"error": "invalid or expired token"}

    r.delete(f"magic:{token}")

    sid = create_session(int(user_id), r=r)

    # Decide `secure` at request time to avoid stale, import-time settings.
    env_name = (getenv("ENV_NAME", settings.ENV_NAME) or "").lower()
    secure = env_name not in ("dev", "development", "test", "local")

    response.set_cookie(
        key="sid",
        value=sid,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.SESSION_TTL_DAYS,
        path="/",
    )
    response.status_code = 302
    response.headers["Location"] = settings.FRONTEND_URL
    return response

from typing import Optional

@router.get("/me", summary="Current user (401 if not logged in)")
def me(user_id: int = Depends(current_user_id), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    return {"user": {"id": user.id, "email": user.email, "role_id": user.role_id}} if user else {"user": None}


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    r: Redis = Depends(get_redis),
):
    sid = request.cookies.get("sid")
    if sid:
        destroy_session(sid, r=r)
    # Clear the cookie
    response.delete_cookie(key="sid", path="/")
    return {"ok": True}
