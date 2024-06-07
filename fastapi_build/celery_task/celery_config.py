# -- coding: utf-8 --
# @Time : 2024/5/15 18:29
# @Author : PinBar
# @File : celery_config.py
import os
from celery_task.enums import TASK_QUEUE
from config import settings
from kombu import Queue

os.environ["C_FORCE_ROOT"] = "true"


# CELERY BROKER
broker_url = "redis://:{}@{}:{}/{}".format(
    settings.REDIS_PASSWORD,
    settings.REDIS_HOST,
    settings.REDIS_PORT,
    settings.REDIS_CACHE_DB,
)
# CELERY BACKEND
result_backend = "redis://:{}@{}:{}/{}".format(
    settings.REDIS_PASSWORD,
    settings.REDIS_HOST,
    settings.REDIS_PORT,
    settings.REDIS_CACHE_DB,
)
# celery task serializer method
task_serializer = "pickle"
# celery result serializer method
result_serializer = "pickle"
# accept content
accept_content = ["pickle"]
# result accept content
result_accept_content = ["pickle"]
# celery result expirations
result_expires = 60 * 2  # 2 minute
# put the acks after completed the task
task_asks_late = True

# TRANSPORT TIMEOUT
RESULT_BACKEND_TRANSPORT_OPTIONS = {"VISIBILITY_TIMEOUT": 3600}  # 1 HOUR.
worker_max_tasks_per_child = 1000
# 非常重要,有些情况下可以防止死锁
celeryd_force_execv = True
# 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死
task_time_limit = 60 * 5


task_queues = (  # 设置add队列,绑定routing_key
    Queue(TASK_QUEUE, routing_key=TASK_QUEUE),
)

task_routes = {}  # projq.tasks.add这个任务进去add队列并routeing_key为xue.add

timezone = "Asia/Shanghai"
CELERY_enable_utc = True
worker_hijack_root_logger = False
# Import the task modules.
imports = ["celery_task.tasks.demo"]
