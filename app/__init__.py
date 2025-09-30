# app/__init__.py
import os
from flask import Flask
from .routes import register_routes
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})  # relax for dev; tighten in prod
    # Example config from env
    app.config["ENV_NAME"] = os.environ.get("ENV", "dev")
    app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
    app.config["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    # Register routes/blueprints
    register_routes(app)
    return app
