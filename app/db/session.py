# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=50,          # Max connections in pool (adjust based on DB max_connections)
    max_overflow=20,       # Additional connections if pool exhausted
    pool_timeout=5,        # Fail fast if no connection available
    pool_recycle=300,      # Recycle connections after 5 minutes to avoid stale
    pool_pre_ping=True,    # Test connections for liveness before use
    pool_use_lifo=False,   # FIFO for better fairness under load
    connect_args={
        "server_settings": {
            "application_name": "fastapi_app",  # Helps DB monitoring
            "statement_timeout": "5000",        # 5s query timeout
        }
    },
    # For PostgreSQL: use asyncpg-specific optimizations
    connect_args={"server_side_params": True},
)
