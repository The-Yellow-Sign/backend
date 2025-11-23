import logging
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.settings import settings

logger = logging.getLogger(__name__)

try:
    async_engine = create_async_engine(
        url=settings.DATABASE_URL.get_secret_value(), echo=False, pool_pre_ping=True
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

except Exception as e:
    logger.critical(f"Could not connect to database: {e}")
    raise e


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_exc:
            await session.rollback()
            logger.error(f"SQLAlchemy error: {sql_exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
            ) from sql_exc
        except HTTPException as http_exc:
            await session.rollback()
            raise http_exc
        except Exception as e:
            await session.rollback()
            logger.error(f"Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            ) from e
        finally:
            pass
