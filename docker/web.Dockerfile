# ---- base ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# ---- deps ----
FROM base AS deps
COPY app/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- runtime ----
FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin
COPY app /app
COPY docker/gunicorn_conf.py /etc/gunicorn/gunicorn_conf.py

EXPOSE 8000
ENV PYTHONPATH=/

# Copy entrypoint script into image
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

CMD ["gunicorn", "app.wsgi:app", "-k", "uvicorn.workers.UvicornWorker", "-c", "/etc/gunicorn/gunicorn_conf.py"]
