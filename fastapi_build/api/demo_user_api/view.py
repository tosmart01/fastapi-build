# -- coding: utf-8 --
# @Time : 2024/5/24 14:42
# @Author : PinBar
# @File : demo.py
from anyio.lowlevel import RunVar
from fastapi import Depends

from auth.hashers import verify_password, create_access_token
from .request_schema import UserQueryParams, UserCreateModel, UserLoginModel, UserLoginResponseModel
from .response_schema import UserListResponse, UserItemResponse
from auth.authenticate import login_required
from core.decorator import api_description
from core.base_view import BaseView
from db.models.user import User
from core.response import Res
from exceptions.custom_exception import PasswordError


class DemoView(BaseView):
    method_decorators = [login_required, ]

    @api_description(summary="用户详情", response_model=Res(UserItemResponse))
    async def detail(self, _id: int):
        user = User.objects.get(User.id == _id, raise_not_found=True)
        return self.message(data=user)

    @api_description(summary="用户查询", response_model=Res(UserListResponse))
    async def get(self, query: UserQueryParams = Depends(UserQueryParams)):
        total, users = await User.objects.search(query)
        return self.message(data={'total': total, 'results': users})

    @api_description(summary="用户创建", response_model=Res(UserItemResponse))
    async def post(self, body: UserCreateModel):
        user = await User.objects.a_create(**body.model_dump())
        return self.message(data=user)

    @api_description(summary="用户更新")
    def put(self,):
        ...

    @api_description(summary="用户删除")
    def delete(self,):
        ...

    @api_description(summary="用户批量更新")
    def multi_put(self,):
        ...

    @api_description(summary="用户批量删除")
    def multi_delete(self,):
        ...


class LoginView(BaseView):
    @api_description(summary="登录")
    def post(self, body: UserLoginModel) -> Res(UserLoginResponseModel):
        user: User = User.objects.get(User.username == body.username, raise_not_found=True)
        if verify_password(body.password, user.password):
            token = create_access_token({"user_id": user.id, "username": user.username})
            return self.message(data={**user.to_dict(), "token": token})
        else:
            raise PasswordError()
