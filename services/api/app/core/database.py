from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# ─── Engine ───────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.API_DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ─── Session factory ──────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ─── Base para modelos ORM ────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Inicializar tablas ───────────────────────────────
async def init_db():
    """Crea todas las tablas si no existen"""
    from app.models import reading, device  # noqa: F401 — registra los modelos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database.initialized", url=settings.DATABASE_URL.split("@")[1])


# ─── Dependency FastAPI ───────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ─── Context manager para uso interno (MQTT, etc.) ───
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
