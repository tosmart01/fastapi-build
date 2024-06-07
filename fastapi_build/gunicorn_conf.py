# -- coding: utf-8 --
# @Time : 2024/5/17 18:02
# @Author : PinBar
# @File : gunicorn_conf.py
from common.log import logger
loglevel = "info"
errorlog = "-"
accesslog = "-"
workers = 5
bind = "0.0.0.0:10001"
worker_class = "uvicorn.workers.UvicornWorker"
