# -- coding: utf-8 --
# @Time : 2024/7/8 10:38
# @Author : zhuo.wang
# @File : context.py
import contextvars


class ContextVarsManager:
    def __init__(self):
        # 初始化一个字典来存储上下文变量
        self._context_vars = {}

    def __getattr__(self, name):
        # 获取上下文变量的值，如果不存在则创建一个新的上下文变量
        if name not in self._context_vars:
            raise AttributeError()
        return self._context_vars[name].get()

    def __setattr__(self, name, value):
        if name == '_context_vars':
            super().__setattr__(name, value)
        else:
            if name not in self._context_vars:
                self._context_vars[name] = contextvars.ContextVar(name)
            self._context_vars[name].set(value)

    def __delattr__(self, name):
        # 删除上下文变量的值，如果存在
        if name in self._context_vars:
            del self._context_vars[name]
        else:
            raise AttributeError(f"'ContextVarsManager' object has no attribute '{name}'")


g = ContextVarsManager()
