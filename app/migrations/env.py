# alembic/env.py
from __future__ import annotations

import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy import engine_from_config

from alembic import context

# --- Logging config (from alembic.ini) ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Load DB URL ---
# Prefer DATABASE_URL environment variable; falls back to alembic.ini's sqlalchemy.url
db_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not db_url:
    raise RuntimeError("No DATABASE_URL set and sqlalchemy.url missing in alembic.ini")

config.set_main_option("sqlalchemy.url", db_url)

# --- Import your models' metadata ---
# Make sure app is importable (working dir should be project root)
from app.models import Base  # Base = DeclarativeBase, and app/models/__init__.py imports User, Role, etc.

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode' (no DBAPI connection)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,         # detect column type changes
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode' (with DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
