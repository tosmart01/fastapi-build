#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: base.py
Time: 2024/12/6
"""
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.append(Path(__file__).parent.parent.as_posix())

from sqlalchemy import String, Integer, DATETIME, text
from sqlalchemy.orm import mapped_column, Mapped

from core.context import g
from db.database import session_maker_sync, session_maker, engine_sync
from models.base import BaseModel, Base


class User(BaseModel):
    __tablename__ = 'user_test'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True, unique=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    creator_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=lambda: getattr(g, 'user_id', None)
    )
    created_time: Mapped[Optional[datetime]] = mapped_column(
        DATETIME(3),
        default=datetime.now,
        nullable=True
    )

@asynccontextmanager
async def with_session():
    try:
        session = session_maker_sync()
        g.session_sync = session
        g.session = session_maker()
        yield
    except Exception:
        g.session_sync.rollback()
        await g.session.rollback()
        raise
    finally:
        g.session_sync.close()
        await g.session.close()



class BaseTest:
    def setup_class(self):
        from db.database import session_maker_sync
        session = session_maker_sync()
        Base.metadata.create_all(bind=engine_sync)
        session.execute(text("truncate table user_test"))

    async def run(self):
        self.setup_class()
        for func in self.__dir__():
            if func.startswith("test"):
                async with with_session():
                    await getattr(self, func)()

