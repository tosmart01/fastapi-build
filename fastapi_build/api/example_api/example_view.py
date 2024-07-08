# -- coding: utf-8 --
# @Time : 2024/6/6 10:41
# @Author : PinBar
# @File : example.py
from typing import Annotated

from fastapi import Request, Query

from core.base_view import BaseView
from core.decorator import api_description
from core.response import Res
from .response_schema import ExampleResponseModel
from .request_schema import ExampleRequestModel


class ExampleView(BaseView):

    @api_description(summary='example view get query', response_model=Res(ExampleResponseModel))
    def get(self, name: Annotated[str, Query(description='名称', min_length=1)]):
        return self.message(data={"name": name, "creator_id": 1})

    @api_description(summary='example view detail query', response_model=Res(ExampleResponseModel))
    async def detail(self, _id: int):
        return self.message(data={"name": 'hello', "creator_id": _id})

    async def post(self, data: ExampleRequestModel) -> Res(ExampleResponseModel):
        return self.message(data={"name": data.name, "creator_id": data.creator_id})
