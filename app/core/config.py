import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV_NAME: str = os.getenv("ENV", "dev")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    BACKEND_PUBLIC_URL: str = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")

    # email
    EMAIL_MODE: str = os.getenv("EMAIL_MODE", "console")  # "console" | "smtp"
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", "noreply@example.com")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "25"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "false").lower() == "true"
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")

    # auth
    MAGIC_TOKEN_TTL: int = int(os.getenv("MAGIC_TOKEN_TTL", "900"))
    SESSION_TTL_DAYS: int = int(os.getenv("SESSION_TTL_DAYS", "30"))

settings = Settings()
