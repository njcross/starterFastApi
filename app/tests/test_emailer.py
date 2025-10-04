import types
from app.core import emailer as em

def test_send_magic_link_uses_smtp(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None): sent["init"] = (host, port, timeout)
        def __enter__(self): sent["enter"] = True; return self
        def __exit__(self, *a): sent["exit"] = True
        def ehlo(self): sent["ehlo"] = sent.get("ehlo", 0) + 1
        def starttls(self): sent["tls"] = True
        def login(self, u, p): sent["login"] = (u, p)
        def send_message(self, msg):
            sent["mail"] = {"from": msg["From"], "to": msg["To"], "subject": msg["Subject"], "body": msg.get_content()}

    # Patch settings attributes directly (no reload needed)
    monkeypatch.setattr(em, "settings", types.SimpleNamespace(
        EMAIL_MODE="smtp",
        EMAIL_SENDER="no-reply@example.com",
        SMTP_HOST="smtp.example",
        SMTP_PORT=587,
        SMTP_TLS=True,
        SMTP_USER="u",
        SMTP_PASS="p",
    ), raising=True)

    em.send_email("alice@example.com", "Subject", "Body", smtp_factory=FakeSMTP)

    assert sent["init"] == ("smtp.example", 587, 10)
    assert sent["enter"] and sent["exit"]
    assert sent["ehlo"] >= 1
    assert sent["tls"] is True
    assert sent["login"] == ("u", "p")
    assert sent["mail"]["from"] == "no-reply@example.com"
    assert sent["mail"]["to"] == "alice@example.com"
    assert sent["mail"]["subject"] == "Subject"
    assert "Body" in sent["mail"]["body"]
