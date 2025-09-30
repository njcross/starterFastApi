from flask import Flask
from .health_routes import bp as health_bp

def register_routes(app: Flask):
    # Infra routes
    app.register_blueprint(health_bp, url_prefix="/api")
