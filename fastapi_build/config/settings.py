# -- coding: utf-8 --
# @Time : 2024/5/15 18:11
# @Author : PinBar
# @File : settings.py
import os
import sys
from pathlib import Path

import pytz
import dotenv
dotenv.load_dotenv()

# BASE_DIR
BASE_DIR = str(Path(__file__).parent.parent.resolve())
# 将BASE_DIR 假如搜索路径
sys.path.insert(0, BASE_DIR)
# [BASE]
ENV = os.getenv("ENV", 'dev')
TZ = pytz.timezone(os.getenv("TZ", "Asia/Shanghai"))
# [REDIS]
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "123456")

# [database]
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", 3306))
DATABASE_USER = os.getenv("DATABASE_USER", "")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", 'database.db')
DATABASE_CHARSET = os.getenv("DATABASE_CHARSET", "utf8mb4")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "")
DATABASE_ASYNC_ENABLED = int(os.getenv("DATABASE_ASYNC_ENABLED", 1))


CREATE_DEPENDS_SESSION = int(os.getenv("CREATE_DEPENDS_SESSION", 1))

# [es]
ES_HOST = os.getenv("ES_HOST", "http://127.0.0.1:9200")
ES_USER = os.getenv("ES_USER", "elastic")
ES_AUTH = int(os.getenv("ES_AUTH", 0))
ES_PASSWORD = os.getenv("ES_PASSWORD", "")

PROJECT_NAME = os.getenv("PROJECT_NAME", "")

LOG_DIR = os.getenv("LOG_DIR", "log")
SECRET_KEY = os.getenv("SECRET_KEY", "")
TOKEN_EXPIRE_SECONDS = int(os.getenv("TOKEN_EXPIRE_SECONDS", 3600 * 24 * 7))
# [gunicorn & fastapi]
USE_GUNICORN_WORKER = int(os.getenv("USE_GUNICORN_WORKER", 0))
SYNC_THREAD_COUNT = int(os.getenv("SYNC_THREAD_COUNT", 800))

# 根据开发环境导入不同配置文件
try:
    if ENV.lower() != "prod":
        exec(f"from config.{ENV} import *")
except ModuleNotFoundError as e:
    print(f"custom settings load fail:{e}")

