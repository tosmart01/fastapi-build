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
    **dict(
        pool_size=20,
        max_overflow=15,
        pool_timeout=15,
    ) if not DB_URL.startswith("sqlite") else {},
    echo=False
)
session_maker_sync = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)

engine = create_async_engine(
    url=ASYNC_DB_URL,
    **dict(
        pool_size=20,
        max_overflow=15,
        pool_timeout=15,
    ) if not ASYNC_DB_URL.startswith("sqlite") else {},
    echo=False,
)
session_maker = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class DatabaseSessionManager:
    def __init__(self):
        self.engine = engine
        self.session_maker = session_maker
        self.engine_sync = engine_sync
        self.session_maker_sync = session_maker_sync

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self.session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self.session_maker()
        try:
            yield session
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    @contextlib.asynccontextmanager
    async def session_sync(self) -> Iterator[Session]:
        session = await run_in_threadpool(lambda: self.session_maker_sync())
        try:
            yield session
        except Exception:
            await run_in_threadpool(lambda: g.session_sync.rollback())
            raise
        finally:
            await run_in_threadpool(lambda: g.session_sync.close())

    async def get_db(self):
        async with self.session() as session: # noqa
            g.session = session
            yield session

    async def get_db_sync(self):
        async with self.session_sync() as session: # noqa
            g.session_sync = session
            yield session

    @contextlib.asynccontextmanager
    async def bind_session(self):
        session = self.session_maker()
        g.session = session
        try:
            yield session
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    @contextlib.contextmanager
    def bind_session_sync(self):
        session = self.session_maker_sync()
        g.session_sync = session
        try:
            yield session
        except Exception:
            g.session_sync.rollback()
            raise
        finally:
            g.session_sync.close()


sessionmanager = DatabaseSessionManager()


def load_sync_session_context(func):
    def wrapper(*args, **kwargs):
        session = sessionmanager.session_maker_sync()
        g.session_sync = session
        try:
            return func(*args, **kwargs)
        except Exception:
            g.session_sync.rollback()
            raise
        finally:
            g.session_sync.close()

    return wrapper


def load_session_context(func):
    async def wrapper(*args, **kwargs):
        session = sessionmanager.session_maker()
        g.session = session
        try:
            return await func(*args, **kwargs)
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    return wrapper


session_type = Annotated[AsyncSession, Depends(sessionmanager.get_db)]
session_type_sync = Annotated[AsyncSession, Depends(sessionmanager.get_db_sync)]
