from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request
from jwt import InvalidTokenError
from passlib.context import CryptContext

from auth.base_authentication import BaseTokenAuthentication
from config.settings import SECRET_KEY
from models.user import User
from exceptions.custom_exception import PermissionDenyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except InvalidTokenError:
        raise PermissionDenyError("Invalid token")
    user = User.objects.get_by_id(user_id)
    if user is None:
        raise PermissionDenyError("用户不存在")
    return user


async def aget_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except InvalidTokenError:
        raise PermissionDenyError("Invalid token")
    user = await User.objects.aget_by_id(user_id)
    if user is None:
        raise PermissionDenyError("用户不存在")
    return user


class TokenAuthentication(BaseTokenAuthentication):

    async def authenticate(self, request: Request):
        token = self.get_jwt_value(request)
        user = await aget_current_user(token)
        return user

    def authenticate_sync(self, request: Request, ):
        token = self.get_jwt_value(request)
        user = get_current_user(token)
        return user
