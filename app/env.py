# migrations/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from app.config import Settings
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
fileConfig(config.config_file_name)

target_metadata = None
# import your SQLAlchemy Base metadata, e.g.:
# from app.db.models import Base
# target_metadata = Base.metadata

settings = Settings()

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
