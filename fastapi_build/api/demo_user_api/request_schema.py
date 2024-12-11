# -- coding: utf-8 --
# @Time : 2024/5/16 11:00
# @Author : PinBar
# @File : schema.py
from typing import Optional

from pydantic import BaseModel, Field, constr, field_validator

from exceptions.custom_exception import ParamsError


class UserCreateModel(BaseModel):
    username: Optional[constr(min_length=1, strip_whitespace=True)] = Field(description='username')
    nickname: str = Field(description='nickname')
    email: Optional[str] = None

    @field_validator('username', mode='after')
    @classmethod
    def name_validator(cls, name: str):
        if ' ' in name:
            raise ParamsError("The name cannot contain spaces")
        return name


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserLoginResponseModel(BaseModel):
    user_id: int = Field(alias='id')
    username: str
    email: str
    token: str
