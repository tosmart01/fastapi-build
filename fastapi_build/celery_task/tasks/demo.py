# -- coding: utf-8 --
# @Time : 2024/5/15 18:34
# @Author : PinBar
# @File : upload.py
from celery_task.celery_app import celery_app
from celery_task.enums import TASK_QUEUE
from common.log import logger


@celery_app.task(queue=TASK_QUEUE, time_limit=3600)
def demo_task():
    logger.info(f"demo_task start")
    return 'success'
