# -- coding: utf-8 --
# @Time : 2024/7/12 00:05
# @Author : zhuo.wang
# @File : base_permission.py
import inspect

from fastapi import Request


class BasePermission:

    def __init__(self, func):
        self.func = func

    def has_permission_sync(self, request: Request):
        raise NotImplementedError()

    async def has_permission(self, request: Request):
        raise NotImplementedError()

    async def __call__(self, request: Request):
        if inspect.iscoroutinefunction(self.func):
            await self.has_permission(request)
        else:
            self.has_permission_sync(request)
