# -- coding: utf-8 --
# @Time : 2024/5/24 17:10
# @Author : PinBar
# @File : response_schema.py
from typing import Optional
from pydantic import BaseModel


class UserItemResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: Optional[str]
    creator_id: Optional[int]
    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    total: int = 0
    results: list[UserItemResponse] = []

    class Config:
        orm_mode = True