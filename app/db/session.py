from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ✅ Engine configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,                  # Disable SQL echo in production
    pool_size=50,                # Max connections in pool
    max_overflow=20,             # Temporary overflow connections
    pool_timeout=5,              # Fail fast if pool exhausted
    pool_recycle=300,            # Recycle connections every 5 min
    pool_pre_ping=True,          # Check connection health before use
    connect_args={
        "server_settings": {
            "application_name": "fastapi_app",
            "statement_timeout": "5000",  # 5s query timeout
        }
    },
)

# ✅ Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ✅ Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
