# -- coding: utf-8 --
# @Time : 2024/5/27 11:42
# @Author : PinBar
# @File : user.py
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.context import g
from models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

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
        DateTime,
        default=datetime.now,
        nullable=True
    )

