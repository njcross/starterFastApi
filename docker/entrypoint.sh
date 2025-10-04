#!/usr/bin/env bash
set -euo pipefail

# Optional: only run migrations when this flag is true (handy for prod)
: "${MIGRATE_ON_START:=true}"

echo "[web] Waiting for Postgres at: ${DATABASE_URL:-<missing>}"
python - <<'PY'
import os, time, sys
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

engine = create_engine(url, pool_pre_ping=True, future=True)

for i in range(60):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("DB is up")
        break
    except Exception as e:
        print(f"DB not ready ({i+1}/60): {e}")
        time.sleep(1)
else:
    print("DB never became ready", file=sys.stderr)
    sys.exit(1)
PY


if [ "${MIGRATE_ON_START}" = "true" ]; then
  pwd
  echo "[web] Running alembic upgrade head…"
  alembic upgrade head
else
  echo "[web] Skipping migrations (MIGRATE_ON_START=${MIGRATE_ON_START})"
fi

echo "[web] Starting Gunicorn…"
exec gunicorn app.wsgi:app -k uvicorn.workers.UvicornWorker -c /etc/gunicorn/gunicorn_conf.py
