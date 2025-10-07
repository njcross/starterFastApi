from pydantic import BaseModel

class HealthResponse(BaseModel):
    ok: bool

class RedisPingResponse(BaseModel):
    redis: str

class DBVersionResponse(BaseModel):
    postgres_version: str

class ErrorResponse(BaseModel):
    error: str
