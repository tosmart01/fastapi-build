# -- coding: utf-8 --
# @Time : 2024/5/15 18:29
# @Author : PinBar
# @File : celery_app.py
from celery import Celery

from common.log import register_logger

celery_app = Celery("app")
celery_app.config_from_object("celery_task.celery_config")

register_logger()

celery_app.conf.beat_schedule = {}

