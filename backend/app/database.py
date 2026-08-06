"""SQLAlchemy async database engine and session factory."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error — rolling back: %s", e, exc_info=True)
            await session.rollback()
            raise


async def create_tables():
    """Create all tables and run lightweight migrations on startup via lifespan."""
    logger.info("Creating database tables if they don't exist...")
    try:
        async with engine.begin() as conn:
            from . import models  # noqa: ensure models are registered
            await conn.run_sync(Base.metadata.create_all)
            
            # Migration: Add user_id column to existing chunking_results table if missing
            from sqlalchemy import text
            await conn.execute(
                text("ALTER TABLE chunking_results ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;")
            )
        logger.info("Database tables and schema initialized successfully.")
    except Exception as e:
        logger.error("Failed to create/migrate database tables: %s", e, exc_info=True)
        raise
