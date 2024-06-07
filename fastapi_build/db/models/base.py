# -- coding: utf-8 --
# @Time : 2024/5/27 11:22
# @Author : PinBar
# @File : base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import Column, Boolean

from db.backends.mysql import session, engine, async_session
from dao.base import BaseDao


class CustomDeclarativeMeta(DeclarativeMeta):

    def __init__(self, *args, **kwargs):
        super(CustomDeclarativeMeta, self).__init__(*args, **kwargs)
        if hasattr(self, 'objects'):
            self.objects.model_cls = self
            self.objects.base_filter = (self.objects.model_cls.is_delete == 0,)
            self.objects.session = session
            self.objects.async_session = async_session


Base = declarative_base(metaclass=CustomDeclarativeMeta)


class BaseModel(Base):
    """基类表模板"""

    __abstract__ = True
    objects = BaseDao()
    is_delete = Column(Boolean, nullable=False, default=False, comment="是否已删除")

    def to_dict(self, keys=None):
        if keys:
            return {c: getattr(self, c, None) for c in keys}
        else:
            return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


def create_tables():
    Base.metadata.create_all(engine)