# app/core/emailer.py
from typing import Callable, ContextManager, Any
import smtplib
from email.message import EmailMessage
from ..core.config import settings as _settings
from fastapi import logger

# re-export so tests can monkeypatch em.settings
settings = _settings

# locally email goes http://localhost:8025/#
def send_email(
    to_addr: str,
    subject: str,
    body: str,
    *,
    smtp_factory: Callable[..., ContextManager[Any]] = smtplib.SMTP,
) -> None:
    s = settings  # read the module-level (patchable) settings
    if s.EMAIL_MODE.lower() != "smtp":
        logger.logger.info("[EMAIL-CONSOLE] To=%s Subject=%s Body=%s", to_addr, subject, body)
        return

    msg = EmailMessage()
    msg["From"] = s.EMAIL_SENDER
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    with smtp_factory(s.SMTP_HOST, s.SMTP_PORT, timeout=10) as server:
        server.ehlo()
        if s.SMTP_TLS:
            server.starttls()
            server.ehlo()
        if s.SMTP_USER and s.SMTP_PASS:
            server.login(s.SMTP_USER, s.SMTP_PASS)
        server.send_message(msg)
