# -- coding: utf-8 --
# @Time : 2024/5/27 14:10
# @Author : PinBar
# @File : auth.py
import inspect
from functools import wraps

from fastapi import Request

from auth.hashers import verify_password, decode_access_token, create_access_token
from core.context import g
from db.models.user import User
from exceptions.custom_exception import AuthDenyError


def get_current_user(user_id) -> User:
    return User.objects.get_by_id(user_id, raise_not_found=True)


async def aget_current_user(user_id) -> User:
    user = await User.objects.aget_by_id(user_id, raise_not_found=True)
    return user


def set_value(user: User, request: Request):
    request.state.user = user
    g.user_id = user.id
    g.user = user


def login_required(func):
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def wrapped_view(*args, **kwargs):
            request = g.request
            token = request.headers.get('Authorization')
            if not token:
                raise AuthDenyError()
            token = token.split('Bearer ')[1].strip()
            try:
                user_info = decode_access_token(token)
            except Exception:
                raise AuthDenyError()
            else:
                user = await aget_current_user(user_info['user_id'])
                set_value(user, request)
                res = await func(*args, **kwargs)
                return res
    else:
        @wraps(func)
        def wrapped_view(*args, **kwargs):
            request = g.request
            token = request.headers.get('Authorization')
            if not token:
                raise AuthDenyError()
            token = token.split('Bearer ')[1].strip()
            try:
                user_info = decode_access_token(token)
            except Exception:
                raise AuthDenyError()
            else:
                user = get_current_user(user_info['user_id'])
                set_value(user, request)
                return func(*args, **kwargs)
    return wrapped_view


def login(username: str, password: str) -> bool:
    user = User.objects.get_by_id(username, id_field='username')
    return verify_password(password, user.password)


if __name__ == '__main__':
    print(create_access_token({"user_id": 1, "username": "user"}, ))
