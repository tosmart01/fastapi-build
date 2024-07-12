# -- coding: utf-8 --
# @Time : 2024/7/11 23:54
# @Author : zhuo.wang
# @File : authentication.py
from fastapi import Request

from auth.base_authentication import BaseTokenAuthentication
from db.models.user import User


class TokenAuthentication(BaseTokenAuthentication):

    async def authenticate(self, request: Request):
        user_info = self.validate_token(request)
        user = await User.objects.aget_by_id(user_info['user_id'])
        return user

    def authenticate_sync(self, request: Request):
        user_info = self.validate_token(request)
        user = User.objects.get_by_id(user_info['user_id'])
        return user
