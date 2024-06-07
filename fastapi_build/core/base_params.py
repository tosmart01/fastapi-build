# -- coding: utf-8 --
# @Time : 2024/5/29 14:36
# @Author : PinBar
# @File : base_params.py
from typing import Annotated
from fastapi import Query


class PaginateParams(object):
    def __init__(self, per_page: Annotated[int, Query(description='每页数量')] = 10,
                 page: Annotated[int, Query(description='页码')] = 1, ):
        self.per_page = per_page
        self.page = page
