import datetime
import uuid
import json
from urllib.parse import urljoin
import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import es_setting
from tests.functional.testdata.es_film_data import film_by_id, all_films_data, rating_test_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'film_id': film_by_id[0]['id']},
                {'status': 200, 'id': film_by_id[0]['id']}
        ),
    ]
)
@pytest.mark.asyncio
async def test_id_film(es_write_data, query_data, expected_answer):
    await es_write_data(film_by_id, 'movies')

    session = aiohttp.ClientSession()
    url = es_setting.service_url + '/api/v1/films/'
    async with session.get(urljoin(url, query_data['film_id'])) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == expected_answer['status']
    assert body['id'] == expected_answer['id']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '-imdb_rating', 'page[size]': 50},
                {'status': 200, 'size': 50}
        ),
    ]
)
@pytest.mark.asyncio
async def test_all_films(es_write_data, query_data, expected_answer):
    await es_write_data(all_films_data, 'movies')

    session = aiohttp.ClientSession()
    url = es_setting.service_url + '/api/v1/films'
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '+imdb_rating', 'page[size]': 2},
                {'status': 200, 'last_rating': 2.0, 'size': 2}
        ),
    ]
)
@pytest.mark.asyncio
async def test_all_films(es_write_data, query_data, expected_answer):
    await es_write_data(rating_test_data, 'movies')

    session = aiohttp.ClientSession()
    url = es_setting.service_url + '/api/v1/films'
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']
    assert body[0]['imdb_rating'] == expected_answer['last_rating']


################################################3

# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [
#         (
#                 {'film_id': film_by_id[0]['id']},
#                 {'status': 200, 'id': film_by_id[0]['id']}
#         ),
#     ]
# )
# @pytest.mark.asyncio
# async def test_id_redis_film(es_del_index, query_data, expected_answer):
#     await es_del_index('movies')
#
#     session = aiohttp.ClientSession()
#     url = es_setting.service_url + '/api/v1/films/'
#     async with session.get(urljoin(url, query_data['film_id'])) as response:
#         body = await response.json()
#         status = response.status
#     await session.close()
#
#     assert status == expected_answer['status']
#     assert body['id'] == expected_answer['id']


