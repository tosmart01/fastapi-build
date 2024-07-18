# -- coding: utf-8 --
# @Time : 2024/7/8 10:38
# @Author : zhuo.wang
# @File : context.py
import contextvars
from typing import Union, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Request

_request = contextvars.ContextVar("request", default=None)
_user_id = contextvars.ContextVar("user_id", default=None)
_user = contextvars.ContextVar("user", default=None)
_session = contextvars.ContextVar("session", default=None)
_extra_data = contextvars.ContextVar("extra_data", default=None)


class ContextVarsManager:
    _support_keys = ("request", "user_id", "user", "extra_data", "session")

    @property
    def request(self) -> Request:
        return _request

    @request.setter
    def request(self, value: Request):
        _request.set(value)

    @property
    def user_id(self) -> Union[int, str, None]:
        return _user_id.get()

    @user_id.setter
    def user_id(self, value: Union[int, str, None]):
        _user_id.set(value)

    @property
    def user(self) -> Union[Any, BaseModel]:
        return _user.get()

    @user.setter
    def user(self, value: Union[Any, BaseModel]):
        _user.set(value)

    @property
    def session(self) -> AsyncSession:
        return _session.get()

    @session.setter
    def session(self, value: AsyncSession):
        _session.set(value)

    @property
    def extra_data(self) -> dict:
        return _extra_data.get()

    @extra_data.setter
    def extra_data(self, value: dict):
        _extra_data.set(value)

    def __setattr__(self, name: str, value: Any):
        if name not in self._support_keys:
            raise ValueError(f"Invalid key {name}, supported keys: {'、'.join(self._support_keys)}")
        return object.__setattr__(self, name, value)


g = ContextVarsManager()
