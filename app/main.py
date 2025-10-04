# app/main.py
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine
from .models import Base

from .core.config import settings

app = FastAPI(
    title="Five Eyes API",
    version="1.0.0",
    description="Endpoints for auth, health checks, etc.",
    contact={"name": "Five Eyes LTD", "email": "dev@example.com"},
    license_info={"name": "MIT"},
    docs_url="/docs",          # change or disable with None
    redoc_url="/redoc",        # change or disable with None
    openapi_url="/openapi.json" # change or disable with None
)

# CORS (allow credentials)
fe_url = settings.FRONTEND_URL
u = urllib.parse.urlparse(fe_url)
fe_origin = f"{u.scheme}://{u.hostname}{'' if (u.port in (None, 80, 443)) else f':{u.port}'}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[fe_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from .routes.health import router as health_router
from .routes.auth import router as auth_router
from .routes.protected import router as protected_router

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(protected_router)
