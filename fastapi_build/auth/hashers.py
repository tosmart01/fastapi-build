# -- coding: utf-8 --
# @Time : 2024/5/27 15:04
# @Author : PinBar
# @File : hashers.py
import time
from typing import TypedDict, Union

import jwt
from passlib.context import CryptContext

from config.settings import SECRET_KEY, TOKEN_EXPIRE_SECONDS
from exceptions.custom_exception import AuthDenyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(TypedDict):
    user_id: Union[int, str]
    username: str
    create_time: float
    expires_delta: int


def make_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Union[TokenData, dict], expires_delta: int = TOKEN_EXPIRE_SECONDS) -> str:
    create_time = time.time()
    data['create_time'] = create_time
    data['expires_delta'] = expires_delta
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> TokenData:
    data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    expires_delta = data['expires_delta']
    if time.time() - data['create_time'] > expires_delta:
        raise AuthDenyError()
    return data

