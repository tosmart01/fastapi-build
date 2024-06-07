import redis

from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_CACHE_DB

normal_cache_pool = redis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_CACHE_DB
)
r_cache = redis.StrictRedis(connection_pool=normal_cache_pool)
normal_cache_pool_decode = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_CACHE_DB,
    decode_responses=True,
)
r_cache_decode = redis.StrictRedis(
    connection_pool=normal_cache_pool_decode,
)


def init():
    if not r_cache.ping():
        raise Exception("Redis is not connected")
