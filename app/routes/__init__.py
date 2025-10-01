# app/routes/__init__.py
from flask import Flask
from .health_routes import bp as health_bp
from .auth_routes import bp as auth_bp
from .protected_routes import bp as protected_bp

def register_routes(app: Flask):
    # Each blueprint should already declare its own url_prefix, e.g.:
    # auth_routes -> url_prefix="/api/auth"
    # protected_routes -> url_prefix="/api/protected"
    # health_routes -> either "/api" or "/health" depending on your file
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)
