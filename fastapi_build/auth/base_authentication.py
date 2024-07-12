# -- coding: utf-8 --
# @Time : 2024/5/27 14:10
# @Author : PinBar
# @File : base_authentication.py
import inspect
from typing import TypeVar, Any, Union

from fastapi import Request
from pydantic import BaseModel

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

    def __init__(self, func):
        self.func = func

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

    async def __call__(self, request: Request):
        if inspect.iscoroutinefunction(self.func):
            user = await self.authenticate(request)
        else:
            user = self.authenticate_sync(request)
        self.set_context(request, user)


class BaseTokenAuthentication(BaseAuthentication):
    async def authenticate(self, request):
        return AnonymousUser()

    def authenticate_async(self, request: Request):
        return AnonymousUser()


if __name__ == '__main__':
    print(create_access_token({"user_id": 1, "username": "user"}, ))