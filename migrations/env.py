# env.py → connects Alembic to your models + database
# revision --autogenerate → generates migration file
# upgrade head → actually creates/updates tables

# env.py is the configuration/bridge that tells Alembic what your application's database schema should look like and how to connect to the database.
# SQLAlchemy Models
#       ↓
# Alembic
#       ↓
# Migration file
#       ↓
# PostgreSQL

# Alembic uses deterministic schema comparison and code generation, not an AI/LLM.

# For example:

# Model says: payments table exists
# Database says: payments table doesn't exist
#         ↓
# Alembic deterministically generates:
# CREATE TABLE payments ...
from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

from app.models.base import Base
import app.models

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

'''
        import app.models causes all the model classes in your __init__.py to be imported, so SQLAlchemy registers their tables in Base.metadata.

Then Alembic can compare:

Base.metadata
      ↓
Expected database schema

        VS

PostgreSQL
      ↓
Current database schema

and generate the migration.'''