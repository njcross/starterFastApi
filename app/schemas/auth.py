from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    email: EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role_id: int | None = None
