import os
from flask import jsonify, current_app, Blueprint
import redis
import psycopg

bp = Blueprint("api", __name__)

def get_redis():
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url, decode_responses=True)

def get_db_conn():
    dsn = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/appdb")
    return psycopg.connect(dsn, autocommit=True)

@bp.get("/health")
def health():
    return jsonify({"ok": True})

@bp.get("/ping-redis")
def ping_redis():
    r = get_redis()
    r.set("hello", "world", ex=30)
    return jsonify({"redis": r.get("hello")})

@bp.get("/db-version")
def db_version():
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                row = cur.fetchone()
                return jsonify({"postgres_version": row[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def register_routes(app):
    app.register_blueprint(bp, url_prefix="/api")

