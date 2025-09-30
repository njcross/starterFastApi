# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, ma, migrate, init_redis
from .routes.health_routes import bp as health_bp

def register_routes(app: Flask):
    # Add all blueprints here
    app.register_blueprint(health_bp, url_prefix="/api")

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Config for SQLAlchemy & Redis
    app.config["ENV_NAME"] = os.getenv("ENV", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    app.redis = init_redis(app)

    # Routes / blueprints
    register_routes(app)
    return app