from fastapi import Query, Body

from .request_schema import UserCreateModel
from .response_schema import UserItemResponse
from core.decorator import api_description
from core.base_view import BaseView
from models.user import User
from core.response import Res, ListRes


# from auth.authentication import TokenAuthentication


class DemoView(BaseView):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = []

    @api_description(summary="user detail", response_model=Res(UserItemResponse))
    async def detail(self, _id: int):
        user = await User.objects.aget(User.id == _id, raise_not_found=True)
        # user = User.objects.get(User.id == _id, raise_not_found=True)
        return self.response(data=user)

    async def get(
            self,
            page: int = Query(default=1, ge=1),
            per_page: int = Query(default=10, ge=1),
            search: str = Query(default="string"),
            sort: str = Query(default="-create_time"),
    ) -> ListRes(UserItemResponse):
        total, data = (
            await User.objects.filter(User.nickname.like(f"%{search}%"))
            .order_by(sort)
            .a_pagination(page, per_page)
        )
        # total, data = User.objects.filter(User.nickname.like(f"%{search}%")).order_by(sort).pagination(page, per_page)
        return self.response(data={"total": total, "items": data})

    @api_description(summary="create user", response_model=Res(UserItemResponse))
    async def post(self, body: UserCreateModel):
        user = await User.objects.a_create(**body.model_dump())
        # user = User.objects.create(**body.model_dump())
        return self.response(data=user)

    @api_description(summary="update user")
    async def put(
            self,
            _id: int,
            nickname: str = Body(..., embed=True),
            email: str = Body(..., embed=True),
    ):
        await User.objects.a_update_by_id(
            _id, properties={"nickname": nickname, "email": email}, raise_not_found=True
        )
        # User.objects.update_by_id(_id, properties={'nickname': nickname, 'email': email}, raise_not_found=True)
        return self.response()

    @api_description(summary="delete user")
    def delete(self, _id: int):
        User.objects.soft_delete_by_id(_id, raise_not_found=True)
        return self.response()

    @api_description(summary="multi put")
    def multi_put(
            self,
    ): ...

    @api_description(summary="multi delete")
    def multi_delete(
            self,
    ): ...
