# -- coding: utf-8 --
# @Time : 2024/5/16 11:00
# @Author : PinBar
# @File : schema.py
from typing import Annotated, Optional

from fastapi import Query, Depends
from pydantic import BaseModel, Field, constr, field_validator

from core.base_params import PaginateParams
from exceptions.custom_exception import ParamsError


class UserQueryParams:
    def __init__(self, username: Annotated[str, Query(description='用户名')] = None,
                 email: Annotated[str, Query(description='邮箱')] = None,
                 paginate_params: PaginateParams = Depends()):
        self.username = username
        self.email = email
        self.paginate_params = paginate_params


class UserCreateModel(BaseModel):
    password: str
    username: Optional[constr(min_length=1, strip_whitespace=True)] = Field(description='用户名')
    nickname: str = Field(description='昵称')
    email: Optional[str] = None

    @field_validator('username', mode='after')
    @classmethod
    def name_validator(cls, name: str):
        if ' ' in name:
            raise ParamsError("名称不能包含空格")
        return name

    class Config:
        orm_mode = True


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserLoginResponseModel(BaseModel):
    user_id: int = Field(alias='id')
    username: str
    email: str
    token: str
