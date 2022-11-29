import asyncio
import time

import aioredis
from aioredis.exceptions import ConnectionError as RedisConError

from functional.settings import redis_setting


async def wait_redis():
    redis = aioredis.from_url(f'{redis_setting.scheme}://{redis_setting.host}:{redis_setting.port}',
                              encoding="utf-8",
                              decode_responses=True,
                              )
    while True:
        try:
            await redis.ping()
            break
        except RedisConError:
            time.sleep(1)


if __name__ == '__main__':
    asyncio.run(wait_redis())
