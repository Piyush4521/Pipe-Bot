"""Alembic Migration Environment Configuration."""

from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import get_settings
from app.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
# Respect explicitly passed custom sqlalchemy.url (e.g. in test suites), else default to settings
custom_url = config.get_main_option("sqlalchemy.url")
if not custom_url or "driver://user:pass" in custom_url or "%(sqlalchemy.url)s" in custom_url:
    target_url = settings.resolved_database_url
else:
    target_url = custom_url
config.set_main_option("sqlalchemy.url", target_url)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    custom_url = config.get_main_option("sqlalchemy.url")
    url = target_url if custom_url else settings.resolved_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    custom_url = config.get_main_option("sqlalchemy.url")
    if not custom_url or "driver://user:pass" in custom_url:
        url = settings.resolved_database_url
    else:
        url = custom_url
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
