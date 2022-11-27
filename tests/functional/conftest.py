import asyncio
from urllib.parse import urljoin

import aiohttp
import aioredis
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError

from functional.settings import es_setting, service_setting, redis_setting
from functional.testdata.es_film_data import films_index_body
from functional.utils.es_fill import get_es_bulk_query


@pytest.fixture(scope="session")
def session_event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def es_client(session_event_loop):
    client = AsyncElasticsearch(hosts=f'{es_setting.scheme}://{es_setting.host}:{es_setting.port}',
                                validate_cert=False,
                                use_ssl=False)
    yield client
    session_event_loop.run_until_complete(client.close())


@pytest_asyncio.fixture
def es_write_data(es_client):
    async def inner(data: list[dict], es_index, index_def=films_index_body):
        try:
            await es_client.indices.create(index=es_index, body=index_def)
        except RequestError as e:
            print('index already exists')
        bulk_query = get_es_bulk_query(data=data, es_index=es_index)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(body=str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture
def es_del_index(es_client):
    async def inner(es_index):
        try:
            await es_client.indices.delete(index=es_index)
        except NotFoundError as e:
            print(e)

    return inner


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_get_request(session):
    async def inner(method: str, params: dict | None = None):
        url = urljoin(service_setting.service_url, service_setting.api_version)
        method_url = urljoin(url, method)
        async with session.get(method_url, params=params) as response:
            body = await response.json()
            status = response.status
            return status, body

    return inner


@pytest_asyncio.fixture(scope='session', autouse=True)
async def redis() -> aioredis.Redis:
    redis = aioredis.from_url(f'{redis_setting.scheme}://{redis_setting.host}:{redis_setting.port}',
                              encoding="utf-8",
                              decode_responses=True,
                              )
    await redis.flushall()
    yield redis
    # закрывать соединения редиса не надо - они закрываются автоматически
