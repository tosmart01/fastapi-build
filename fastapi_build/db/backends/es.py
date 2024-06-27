# -- coding: utf-8 --
# @Time : 2024/5/15 18:26
# @Author : PinBar
# @File : es.py
from elasticsearch import Elasticsearch
from elasticsearch import AsyncElasticsearch

from config import settings

if settings.ES_AUTH:
    es = Elasticsearch(settings.ES_HOST, maxsize=30,
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), timeout=30,
                       max_retries=10, retry_on_timeout=True)
    aio_es = AsyncElasticsearch(settings.ES_HOST, http_auth=(settings.ES_USER, settings.ES_PASSWORD), timeout=30,
                                max_retries=10, retry_on_timeout=True )
else:
    es = Elasticsearch(settings.ES_HOST, maxsize=30, timeout=30, max_retries=10, retry_on_timeout=True)
    aio_es = AsyncElasticsearch(settings.ES_HOST,  timeout=30, max_retries=10, retry_on_timeout=True )





