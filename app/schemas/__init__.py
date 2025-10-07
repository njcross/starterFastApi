# app/schemas/__init__.py
from .auth import (
    EmailRequest,
    MagicLinkResponse,
    ErrorResponse,
    MeUser,
    MeResponse,
    LogoutResponse,
    CallbackOK,
)
from .health import (
    HealthResponse, 
    RedisPingResponse,
    DBVersionResponse,
    ErrorResponse
)
from .protected import (
    WhoAmIResponse
)

__all__ = [
    "EmailRequest",
    "MagicLinkResponse",
    "ErrorResponse",
    "MeUser",
    "MeResponse",
    "LogoutResponse",
    "CallbackOK",
    "HealthResponse",
    "RedisPingResponse",
    "DBVersionResponse",
    "ErrorResponse",
    "WhoAmIResponse",
]
