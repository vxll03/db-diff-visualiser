from contextlib import asynccontextmanager
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class DbModel(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


# region Session factory
sync_engine = sa.create_engine(settings.db.SYNC_DATABASE_URL)
engine = create_async_engine(
    settings.db.DATABASE_URL,
    echo=settings.db.ECHO,
)

LocalSessionMaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session():
    async with LocalSessionMaker() as session:
        try:
            yield session
        except Exception:
            try:
                await session.rollback()
            except Exception as rollback_error:
                logger.error(f"Error with database rollback occurred: {rollback_error}")
                await session.close()
            finally:
                raise
        finally:
            try:
                await session.close()
            except Exception as close_error:
                logger.error(
                    f"Error with database session close occurred: {close_error}"
                )
                raise


DatabaseDep = Annotated[AsyncSession, Depends(get_session)]


@asynccontextmanager
async def get_db_context():
    async with LocalSessionMaker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


# endregion
