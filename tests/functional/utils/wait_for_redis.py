import time
from settings import redis_setting
import aioredis

if __name__ == '__main__':
    redis = aioredis.from_url(f'{redis_setting.scheme}://{redis_setting.host}:{redis_setting.port}',
                              encoding="utf-8",
                              decode_responses=True,
                              )
    while True:
        if redis.ping():
            break
        time.sleep(1)
