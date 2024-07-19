# -- coding: utf-8 --
# @Time : 2024/5/27 14:10
# @Author : PinBar
# @File : base_authentication.py
import inspect
from typing import TypeVar, Any, Union

from fastapi import Request
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool

from auth.hashers import create_access_token, decode_access_token
from core.context import g
from exceptions.custom_exception import AuthDenyError

User = TypeVar("User", bound=Any)


class AnonymousUser(BaseModel):
    id: int = -1
    username: str = "AnonymousUser"


def get_current_user(user_id) -> AnonymousUser:
    return AnonymousUser(id=user_id)


async def aget_current_user(user_id) -> AnonymousUser:
    return AnonymousUser(id=user_id)


class BaseAuthentication:

    def __init__(self, name):
        self.name = name

    def set_context(self, request: Request, user):
        g.user = user
        g.user_id = user.id
        g.request = request
        request.state.user_id = user.id
        request.state.user = user

    def authenticate_sync(self, request: Request) -> Union[User, AnonymousUser]:
        raise NotImplementedError()

    async def authenticate(self, request: Request) -> Union[User, AnonymousUser]:
        raise NotImplementedError()

    def __call__(self, func):
        is_async = inspect.iscoroutinefunction(func)
        auth_func = self.authenticate if is_async else self.authenticate_sync

        async def run(request: Request):
            if is_async:
                user = await auth_func(request)
            else:
                user = await run_in_threadpool(auth_func, request)
            self.set_context(request, user)

        return run


class BaseTokenAuthentication(BaseAuthentication):
    def get_jwt_value(self, request: Request) -> str:
        token = request.headers.get('Authorization')
        if not token:
            raise AuthDenyError()
        token = token.split('Bearer ')[1].strip()
        return token

    def validate_token(self, request: Request):
        token = self.get_jwt_value(request)
        try:
            user_info = decode_access_token(token)
        except Exception:
            raise AuthDenyError()
        return user_info

    async def authenticate(self, request):
        return AnonymousUser()

    def authenticate_sync(self, request: Request):
        return AnonymousUser()


if __name__ == '__main__':
    print(create_access_token({"user_id": 1, "username": "user"}, ))
