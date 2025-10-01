# app/routes/auth_routes.py
import os
import smtplib
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify, current_app, redirect, make_response
import jwt  # PyJWT

from .utils import json_required
from ..extensions import db
from ..models import User
from ..schemas.auth import EmailRequestSchema
from ..auth.session import create_session
from email.message import EmailMessage

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def _redis():
    return current_app.redis  # set in app/__init__.py via init_redis

def _send_email(to_addr: str, subject: str, body: str) -> None:
    mode = os.getenv("EMAIL_MODE", "console").lower()  # "smtp" | "console"
    sender = os.getenv("EMAIL_SENDER", "noreply@example.com")

    if mode != "smtp":
        # dev fallback: just log it
        current_app.logger.info("[EMAIL-CONSOLE] To=%s Subject=%s Body=%s", to_addr, subject, body)
        return

    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", "25"))
    use_tls = os.getenv("SMTP_TLS", "true").lower() == "true"
    user = os.getenv("SMTP_USER") or ""
    password = os.getenv("SMTP_PASS") or ""

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=10) as server:
        server.ehlo()
        # MailHog has no STARTTLS; only do this if explicitly enabled
        if use_tls:
            server.starttls()
            server.ehlo()
        # MailHog doesn’t need auth; only login if creds provided
        if user and password:
            server.login(user, password)
        server.send_message(msg)

def _jwt_now():
    return datetime.now(tz=timezone.utc)

def _jwt_issue(user_id: int):
    secret = os.getenv("JWT_SECRET", "dev-not-secret")
    ttl_days = int(os.getenv("SESSION_TTL_DAYS", "30"))
    exp = _jwt_now() + timedelta(days=ttl_days)
    return jwt.encode({"sub": user_id, "exp": exp}, secret, algorithm="HS256")

@bp.post("/request-link")
@json_required
def request_link():
    # Validate payload
    data = EmailRequestSchema().load(request.get_json() or {})
    email = data["email"].strip().lower()

    # Upsert user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    # Create single-use token in Redis
    token = secrets.token_urlsafe(32)
    ttl = int(os.getenv("MAGIC_TOKEN_TTL", "900"))
    rkey = f"magic:{token}"
    _redis().setex(rkey, ttl, str(user.id))

    # Build link
    backend_public = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    link = f"{backend_public}/api/auth/callback?token={token}"

    # Send email
    _send_email(
        to_addr=email,
        subject="Your sign-in link",
        body=f"Click to sign in: {link}\n\nThis link expires in {ttl // 60} minutes.",
    )

    return jsonify({"sent": True})

@bp.get("/callback")
def callback():
    token = request.args.get("token", "")
    if not token:
        return jsonify({"error": "missing token"}), 400

    rkey = f"magic:{token}"
    user_id = _redis().get(rkey)
    if not user_id:
        return jsonify({"error": "invalid or expired token"}), 400

    # consume the single-use magic token
    _redis().delete(rkey)

    # create a server-side session (Redis) and set cookie
    sid = create_session(int(user_id))

    resp = make_response(redirect(os.getenv("FRONTEND_URL", "http://localhost:5173")))
    secure = (current_app.config.get("ENV_NAME") not in ("dev", "development", "test"))
    resp.set_cookie(
        "sid",
        sid,
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=60 * 60 * 24 * int(os.getenv("SESSION_TTL_DAYS", "30")),
        path="/",
    )
    return resp

@bp.get("/me")
def me():
    """Optional: resolve the session cookie to the current user."""
    secret = os.getenv("JWT_SECRET", "dev-not-secret")
    token = request.cookies.get("session")
    if not token:
        return jsonify({"authenticated": False}), 200
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user = db.session.get(User, int(payload["sub"]))
        if not user:
            return jsonify({"authenticated": False}), 200
        return jsonify({"authenticated": True, "email": user.email})
    except jwt.ExpiredSignatureError:
        return jsonify({"authenticated": False, "error": "expired"}), 200
    except Exception:
        return jsonify({"authenticated": False}), 200
