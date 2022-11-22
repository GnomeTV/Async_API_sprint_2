import asyncio
from typing import List

import aiohttp
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError
import pytest
import pytest_asyncio
from settings import es_setting
from testdata.es_film_data import films_index_body
from utils.es_fill import get_es_bulk_query


@pytest.fixture(scope="session")
def session_event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def es_client(session_event_loop):
    client = AsyncElasticsearch(hosts=es_setting.es_host,
                                validate_cert=False,
                                use_ssl=False)
    yield client
    session_event_loop.run_until_complete(client.close())


@pytest_asyncio.fixture
def es_write_data(es_client):
    async def inner(data: List[dict], es_index):
        try:
            await es_client.indices.create(index=es_index, body=films_index_body)
        except RequestError as e:
            print('index already exist')
        bulk_query = get_es_bulk_query(data=data, es_index=es_index)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


# @pytest_asyncio.fixture
# def es_del_index(es_client):
#     async def inner(es_index):
#         try:
#             await es_client.indices.delete(index=es_index)
#         except NotFoundError as e:
#             print(e)
#     return inner