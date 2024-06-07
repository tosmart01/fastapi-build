# -- coding: utf-8 --
# @Time : 2024/6/6 10:41
# @Author : PinBar
# @File : request_schema.py
from pydantic import BaseModel, Field, field_validator
from exceptions.custom_exception import ParamsError


class ExampleRequestModel(BaseModel):
    name: str
    creator_id: int = Field(description='创建人', gt=1)

    @field_validator('name', mode='after')
    @classmethod
    def name_validator(cls, name: str):
        if ' ' in name:
            raise ParamsError("名称不能包含空格")
        return name

