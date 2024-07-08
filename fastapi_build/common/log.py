# -- coding: utf-8 --
# @Time : 2024/5/15 18:34
# @Author : PinBar
# @File : logger.py
import os
import sys
import logging

from loguru import logger as flask_logger
from config.settings import LOG_DIR, PROJECT_NAME, USE_GUNICORN_WORKER

logger = flask_logger.bind(is_flask=True)
LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def register_logger():
    """注册日志到loguru，由loguru统一管理日志的格式、旋转、错误等"""
    # [定义日志路径]
    os.makedirs(LOG_DIR, exist_ok=True)
    prefix = f"{PROJECT_NAME}_" if PROJECT_NAME else ""
    intercept_handler = InterceptHandler()
    # logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    # logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout, "level": LOG_LEVEL}])

    # 日志旋转、大小限制、更替等参数均支持多种配置,详情请参考文档
    # [logger参数文档: https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger]
    # 请务必设置colorize=False,避免在不同系统上由于颜色标签的写入造成问题
    logger.add(
        os.path.join(LOG_DIR, prefix, "info_{time:%Y-%m-%d}.log"),
        level="INFO",
        colorize=False,
        rotation="1 days",
        retention="7 days",
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
        format="{time} {level} {message} | PID:{process} | TID: {thread}",
        catch=False,
    )
    logger.add(
        os.path.join(LOG_DIR, prefix, "error_{time:%Y-%m-%d}.log"),
        level="ERROR",
        colorize=False,
        rotation="1 days",
        retention="15 days",
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
        format="{time} {level} {message} | PID:{process} | TID: {thread}",
        catch=False,
    )
    # logger.add(
    #     os.path.join(LOG_DIR, prefix, "error_detail_{time:%Y-%m-%d}.log"),
    #     level="ERROR",
    #     colorize=False,
    #     rotation="1 days",
    #     retention="3 days",
    #     backtrace=True,
    #     diagnose=True,
    #     encoding="utf-8",
    #     format="{time} {level} {message} | PID:{process} | TID: {thread}",
    # )


register_logger()

if USE_GUNICORN_WORKER:
    from gunicorn.glogging import Logger


    class StubbedGunicornLogger(Logger):
        def setup(self, cfg):
            handler = logging.NullHandler()
            self.error_logger = logging.getLogger("gunicorn.error")
            self.error_logger.addHandler(handler)
            self.access_logger = logging.getLogger("gunicorn.access")
            self.access_logger.addHandler(handler)
            self.error_logger.setLevel(LOG_LEVEL)
            self.access_logger.setLevel(LOG_LEVEL)
