# -- coding: utf-8 --
# @Time : 2024/5/27 11:22
# @Author : PinBar
# @File : database.py
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

from db.db_url import build_db_urls
from config.settings import DATABASE_ASYNC_ENABLED
from core.context import g


class DatabaseSessionManager:
    def __init__(self):
        db_url, async_db_url = build_db_urls()

        self.engine_sync = None
        self.session_maker_sync = None
        self.engine_async = None
        self.session_maker_async = None

        # 同步引擎（无论 async 是否开启，都可以创建）
        self.engine_sync = create_engine(
            url=db_url,
            pool_recycle=300,
            **dict(
                pool_size=20,
                max_overflow=15,
                pool_timeout=15,
            ) if not db_url.startswith("sqlite") else {},
            echo=False
        )
        self.session_maker_sync = sessionmaker(bind=self.engine_sync, autocommit=False, autoflush=False)

        # 异步引擎（仅在 async 模式开启时才创建）
        if DATABASE_ASYNC_ENABLED:
            self.engine_async = create_async_engine(
                url=async_db_url,
                **dict(
                    pool_size=20,
                    max_overflow=15,
                    pool_timeout=15,
                ) if not async_db_url.startswith("sqlite") else {},
                echo=False,
            )
            self.session_maker_async = async_sessionmaker(
                bind=self.engine_async,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not DATABASE_ASYNC_ENABLED or self.session_maker_async is None:
            raise RuntimeError("异步数据库未启用")
        session = self.session_maker_async()
        try:
            yield session
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    @contextlib.asynccontextmanager
    async def session_sync(self) -> Iterator[Session]:
        if self.session_maker_sync is None:
            raise RuntimeError("同步数据库未初始化")
        session = await run_in_threadpool(lambda: self.session_maker_sync())
        try:
            yield session
        except Exception:
            await run_in_threadpool(lambda: g.session_sync.rollback())
            raise
        finally:
            await run_in_threadpool(lambda: g.session_sync.close())

    async def get_db(self):
        async with self.session() as session:
            g.session = session
            yield session

    async def get_db_sync(self):
        async with self.session_sync() as session:
            g.session_sync = session
            yield session


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
        if not DATABASE_ASYNC_ENABLED:
            raise RuntimeError("异步数据库未启用")
        session = sessionmanager.session_maker_async()
        g.session = session
        try:
            return await func(*args, **kwargs)
        except Exception:
            await g.session.rollback()
            raise
        finally:
            await g.session.close()

    return wrapper


def load_session():
    if DATABASE_ASYNC_ENABLED:
        g.session = sessionmanager.session_maker_async()
    g.session_sync = sessionmanager.session_maker_sync()


session_type = Annotated[AsyncSession, Depends(sessionmanager.get_db)]
session_type_sync = Annotated[AsyncSession, Depends(sessionmanager.get_db_sync)]
