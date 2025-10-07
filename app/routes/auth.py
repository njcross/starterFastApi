from typing import Optional
from os import getenv
import secrets

from fastapi import APIRouter, Depends, Response, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from redis import Redis

from ..db import get_db
from ..models.user import User
from ..schemas.auth import (
    EmailRequest,
    MagicLinkResponse,
    ErrorResponse,
    MeResponse,
    MeUser,
    LogoutResponse,
    CallbackOK,        # <-- NEW
)
from ..core.redis_client import get_redis
from ..auth.session import create_session, destroy_session
from ..core.config import settings
from ..core.emailer import send_email
from ..auth.deps import current_user_id

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post(
    "/request-link",
    summary="Send magic login link",
    response_model=MagicLinkResponse,
    responses={
        200: {"model": MagicLinkResponse, "description": "Magic link email enqueued"},
        422: {"description": "Validation error"},
    },
)
def request_link(
    payload: EmailRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis),
) -> MagicLinkResponse:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = secrets.token_urlsafe(32)
    r.setex(f"magic:{token}", settings.MAGIC_TOKEN_TTL, str(user.id))

    link = f"{settings.BACKEND_PUBLIC_URL}/api/auth/callback?token={token}"
    background.add_task(
        send_email,
        to_addr=email,
        subject="Your sign-in link",
        body=f"Click to sign in: {link}\n\nThis link expires in {settings.MAGIC_TOKEN_TTL // 60} minutes.",
    )
    return MagicLinkResponse(sent=True)


@router.get(
    "/callback",
    status_code=status.HTTP_302_FOUND,              # default is 302 (redirect)
    response_class=RedirectResponse,
    responses={
        200: {                                      # JSON success (opt-in)
            "model": CallbackOK,
            "description": "JSON success when client requests JSON (Accept: application/json) or ?json=1",
            "headers": {
                "Set-Cookie": {"schema": {"type": "string"}, "description": "Session cookie (sid)"},
            },
        },
        302: {
            "description": "Redirect to frontend",
            "headers": {
                "Location": {"schema": {"type": "string", "format": "uri"}, "description": "Destination URL"},
                "Set-Cookie": {"schema": {"type": "string"}, "description": "Session cookie (sid)"},
            },
        },
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
    },
)
def callback(token: str, request: Request, r: Redis = Depends(get_redis)):
    user_id = r.get(f"magic:{token}")
    if not user_id:
        # make 400 appear with a modeled body
        raise HTTPException(status_code=400, detail="invalid or expired token")

    r.delete(f"magic:{token}")

    sid = create_session(int(user_id), r=r)

    # Decide `secure` at request time
    env_name = (getenv("ENV_NAME", settings.ENV_NAME) or "").lower()
    secure = env_name not in ("dev", "development", "test", "local")

    # Opt-in JSON mode: Accept header or ?json=1
    wants_json = (
        "application/json" in (request.headers.get("accept") or "").lower()
        or request.query_params.get("json") in {"1", "true", "yes"}
    )

    if wants_json:
        resp = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "next": settings.FRONTEND_URL},
        )
    else:
        resp = RedirectResponse(
            url=settings.FRONTEND_URL,
            status_code=status.HTTP_302_FOUND
        )

    resp.set_cookie(
        key="sid",
        value=sid,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.SESSION_TTL_DAYS,
        path="/",
    )
    return resp


@router.get(
    "/me",
    summary="Current user (401 if not logged in)",
    response_model=MeResponse,
    responses={
        200: {"model": MeResponse, "description": "Current user"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
def me(user_id: int = Depends(current_user_id), db: Session = Depends(get_db)) -> MeResponse:
    user = db.get(User, user_id)
    if not user:
        return MeResponse(user=None)
    return MeResponse(user=MeUser(id=user.id, email=user.email, role_id=user.role_id))


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        200: {"model": LogoutResponse, "description": "Logged out and cookie cleared"},
    },
)
def logout(
    request: Request,
    response: Response,
    r: Redis = Depends(get_redis),
) -> LogoutResponse:
    sid = request.cookies.get("sid")
    if sid:
        destroy_session(sid, r=r)
    response.delete_cookie(key="sid", path="/")
    return LogoutResponse(ok=True)
