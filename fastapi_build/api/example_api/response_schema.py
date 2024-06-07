# -- coding: utf-8 --
# @Time : 2024/5/24 17:10
# @Author : PinBar
# @File : response_schema.py
from pydantic import BaseModel


class ExampleResponseModel(BaseModel):
    name: str
    creator_id: int
