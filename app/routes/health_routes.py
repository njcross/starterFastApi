# app/routes/health_routes.py
import os
from flask import jsonify, Blueprint
import redis
import psycopg2

bp = Blueprint("health", __name__, url_prefix="/api")

def get_redis():
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url, decode_responses=True)

def get_db_conn():
    dsn = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
    # add a short connect timeout
    return psycopg2.connect(dsn, connect_timeout=2)

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
        # helpful in dev
        return jsonify({"error": str(e)}), 500
