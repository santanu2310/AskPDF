from typing import Any, TypeAlias
from collections.abc import AsyncGenerator
from fastapi import Request
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine as _create_async_engine,
)
from sqlalchemy.orm import Session

from app.core import sql
from app.core.config import settings


def create_async_engine() -> AsyncEngine:
    connect_args: dict[str, Any] = {}
    connect_args["command_timeout"] = settings.DATABASE_COMMAND_TIMEOUT_SECONDS

    return _create_async_engine(
        str(settings.get_postgres_dsn("asyncpg")),
        echo=settings.SQLALCHEMY_DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_recycle=settings.DATABASE_POOL_RECYCLE_SECONDS,
    )


AsyncSessionMaker: TypeAlias = async_sessionmaker[AsyncSession]


def create_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db(request: Request) -> AsyncGenerator[AsyncSession]:
    try:
        sessionmaker = request.state.db
    except AttributeError as e:
        raise RuntimeError(
            "Session is not present in the request state. "
            "Did you forget to add AsyncSessionMiddleware?"
        ) from e
    async with sessionmaker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


__all__ = [
    "AsyncSession",
    "AsyncEngine",
    "Session",
    "Engine",
    "AsyncSessionMaker",
    "create_async_engine",
    "create_async_sessionmaker",
    "get_db",
    "sql",
]
