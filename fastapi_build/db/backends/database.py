# -- coding: utf-8 --
# @Time : 2024/5/27 11:22
# @Author : PinBar
# @File : database.py
import contextlib
from typing import AsyncIterator, Annotated, Iterator

from fastapi import Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from config.settings import DB_URL, ASYNC_DB_URL
from core.context import g

engine_sync = create_engine(
    url=DB_URL,
    pool_recycle=300,
    pool_size=20,
    max_overflow=15,
    pool_timeout=15,
    echo=False)
session_maker_sync = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)

engine = create_async_engine(
    url=ASYNC_DB_URL,
    pool_recycle=300,
    pool_size=20,
    max_overflow=10,
    pool_timeout=15,
    echo=False,
)
session_maker = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


class DatabaseSessionManager:
    def __init__(self):
        self._engine = engine
        self._session_maker = session_maker
        self._engine_sync = engine_sync
        self._session_maker_sync = session_maker_sync

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    @contextlib.asynccontextmanager
    async def session_sync(self) -> Iterator[Session]:
        if self._session_maker_sync is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = await run_in_threadpool(lambda: self._session_maker_sync())
        try:
            yield session
        except Exception:
            await run_in_threadpool(lambda: g.session_sync.rollback())
            raise
        finally:
            await run_in_threadpool(lambda: g.session_sync.close())


sessionmanager = DatabaseSessionManager()


async def get_db():
    async with sessionmanager.session() as session:
        g.session = session
        yield session


async def get_db_sync():
    async with sessionmanager.session_sync() as session:
        g.session_sync = session
        yield session


def load_session_context(func):
    def wrapper(*args, **kwargs):
        session = sessionmanager._session_maker_sync()
        g.session_sync = session
        try:
            return func(*args, **kwargs)
        except Exception:
            g.session_sync.rollback()
            raise
        finally:
            g.session_sync.close()

    return wrapper


session_type = Annotated[AsyncSession, Depends(get_db)]
session_type_sync = Annotated[AsyncSession, Depends(get_db_sync)]
