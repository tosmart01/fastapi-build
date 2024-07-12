# -- coding: utf-8 --
# @Time : 2024/7/12 00:05
# @Author : zhuo.wang
# @File : base_permission.py
import inspect

from fastapi import Request


class BasePermission:

    def __init__(self, perm=None):
        self.perm = perm

    def has_permission_sync(self, request: Request) -> bool:
        raise NotImplementedError()

    async def has_permission(self, request: Request) -> bool:
        raise NotImplementedError()

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):
            return self.has_permission
        else:
            return self.has_permission_sync
