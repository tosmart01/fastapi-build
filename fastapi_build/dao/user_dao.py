# -- coding: utf-8 --
# @Time : 2024/5/27 14:59
# @Author : PinBar
# @File : user_dao.py
from typing import Dict, Any, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.demo_user_api.request_schema import UserQueryParams
from auth.hashers import make_password
from exceptions.base import ApiError
from .sql_tools import a_pagination
from .base import BaseDao

if TYPE_CHECKING:
    from db.models.user import User


class UserDao(BaseDao):
    model_cls: "User"

    def create(
            self,
            commit: bool = True,
            **properties: Dict[str, Any],
    ) -> "User":
        password = properties.get("password")
        properties['password'] = make_password(password)
        try:
            return super().create(commit, **properties)
        except IntegrityError:
            raise ApiError(message="用户名重复")

    async def a_create(
            self,
            commit: bool = True,
            **properties: Dict[str, Any],
    ) -> "User":
        password = properties.get("password")
        properties['password'] = make_password(password)
        try:
            user = await super().a_create(commit, **properties)
        except IntegrityError:
            raise ApiError(message="用户名重复")
        return user

    async def search(self, params: UserQueryParams) -> tuple[int, list["User"]]:
        async with self.async_session() as session:
            query = select(self.model_cls).where(*self.base_filter, )
            if params.username:
                query = query.where(self.model_cls.username == params.username)
            if params.email:
                query = query.where(self.model_cls.email == params.email)
            total, result = await a_pagination(session, query=query, per_page=params.paginate_params.per_page,
                                               page=params.paginate_params.page, query_type='model'
                                               )
            return total, result
