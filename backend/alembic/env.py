import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# -------------------------------
# Make "app" importable
# -------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Alembic Config
# -------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------
# Import SQLAlchemy Base metadata
# -------------------------------
from app.models import Base

target_metadata = Base.metadata

# -------------------------------
# Set DATABASE_URL from .env
# -------------------------------
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. Make sure backend/.env exists and contains it."
    )

config.set_main_option("sqlalchemy.url", database_url)


# -------------------------------
# Offline migrations
# -------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------
# Online migrations
# -------------------------------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------
# Entry point
# -------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()