# -- coding: utf-8 --
# @Time : 2024/5/27 11:22
# @Author : PinBar
# @File : mysql.py
import contextlib
from typing import AsyncIterator, Any, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncConnection
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import DB_URL, ASYNC_DB_URL
from core.context import g

engine = create_engine(
    url=DB_URL,
    pool_recycle=300,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    echo=False,
)
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
)
Session = sessionmaker(bind=engine)
session = scoped_session(Session)
async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class DatabaseSessionManager:
    def __init__(self):
        self._engine = async_engine
        self._sessionmaker = async_session_maker

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager()


async def get_db():
    async with sessionmanager.session() as session:
        g.session = session
        yield session

async_session = Annotated[AsyncSession, Depends(get_db)]