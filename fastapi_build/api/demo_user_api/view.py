# -- coding: utf-8 --
# @Time : 2024/5/24 14:42
# @Author : PinBar
# @File : demo.py
from fastapi import Depends, Request

from .request_schema import UserQueryParams, UserCreateModel
from .response_schema import UserListResponse, UserItemResponse
# from auth.authenticate import login_required
from core.decorator import api_description
from core.base_view import BaseView
from db.models.user import User
from core.response import Res


class DemoView(BaseView):
    # method_decorators = [login_required, ]

    @api_description(summary="用户详情", response_model=Res(UserItemResponse))
    def detail(self, request: Request, _id: int):
        user = User.objects.get(User.id == _id, raise_not_found=True)
        return self.message(data=user)

    @api_description(summary="用户查询", response_model=Res(UserListResponse))
    async def get(self, request: Request, query: UserQueryParams = Depends(UserQueryParams)):
        total, users = await User.objects.search(query)
        return self.message(data={'total': total, 'results': users})

    @api_description(summary="用户创建", response_model=Res(UserItemResponse))
    async def post(self, request: Request, body: UserCreateModel):
        user = await User.objects.a_create(**body.model_dump())
        return self.message(data=user)

    @api_description(summary="用户更新")
    def put(self, request: Request):
        ...

    @api_description(summary="用户删除")
    def delete(self, request: Request):
        ...

    @api_description(summary="用户批量更新")
    def multi_put(self, request: Request):
        ...

    @api_description(summary="用户批量删除")
    def multi_delete(self, request: Request):
        ...
