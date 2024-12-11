import redis
import redis.asyncio as aioredis

from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_CACHE_DB

normal_cache_pool = redis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_CACHE_DB
)
normal_cache_pool_decode = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_CACHE_DB,
    decode_responses=True,
)

r_cache = redis.StrictRedis(connection_pool=normal_cache_pool)
r_cache_decode = redis.StrictRedis(
    connection_pool=normal_cache_pool_decode,
)

aio_normal_cache_pool = aioredis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_CACHE_DB
)
aio_normal_cache_pool_decode = aioredis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_CACHE_DB,
    decode_responses=True,
)
aio_r_cache = aioredis.StrictRedis(connection_pool=aio_normal_cache_pool)
aio_r_cache_decode = aioredis.StrictRedis(
    connection_pool=aio_normal_cache_pool_decode,
)

