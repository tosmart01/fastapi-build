# -- coding: utf-8 --
# @Time : 2024/7/8 15:02
# @Author : zhuo.wang
# @File : startup.py


from anyio.lowlevel import RunVar
from anyio import CapacityLimiter
from config.settings import SYNC_THREAD_COUNT


def startup():
    RunVar("_default_thread_limiter").set(CapacityLimiter(SYNC_THREAD_COUNT))
