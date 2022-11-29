import asyncio
import time

import aioredis
from aioredis.exceptions import ConnectionError as RedisConError

from core.config import settings


async def wait_redis():
    redis = aioredis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}",
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
