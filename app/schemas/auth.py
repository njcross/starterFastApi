from pydantic import BaseModel, EmailStr, AnyUrl
from typing import Optional

class EmailRequest(BaseModel):
    email: EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role_id: int | None = None

class EmailRequest(BaseModel):
    email: EmailStr

class MagicLinkResponse(BaseModel):
    sent: bool

class ErrorResponse(BaseModel):
    error: str

class MeUser(BaseModel):
    id: int
    email: EmailStr
    role_id: Optional[int] = None

class MeResponse(BaseModel):
    user: Optional[MeUser]  # None if not found

class LogoutResponse(BaseModel):
    ok: bool

# NEW: used for 200 JSON from /callback
class CallbackOK(BaseModel):
    ok: bool
    next: AnyUrl
