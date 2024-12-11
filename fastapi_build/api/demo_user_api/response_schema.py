# -- coding: utf-8 --
# @Time : 2024/5/24 17:10
# @Author : PinBar
# @File : response_schema.py
from datetime import datetime
from typing import Optional, Union

from core.response import CustomModel


class UserItemResponse(CustomModel):
    id: int
    username: str
    nickname: str
    email: Optional[str]
    creator_id: Optional[int]
    created_time: Union[datetime, None]
