from urllib.parse import urljoin

import pytest

from functional.testdata.es_film_data import film_by_id, all_films_data, rating_test_data

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'film_id': film_by_id[0]['id']},
                {'status': 200, 'id': film_by_id[0]['id']}
        ),
    ]
)
async def test_id_film(make_get_request, es_write_data, query_data, expected_answer):
    await es_write_data(film_by_id, 'movies')

    status, body = await make_get_request(urljoin('films/', query_data['film_id']))

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
async def test_all_films(make_get_request, es_write_data, query_data, expected_answer):
    await es_write_data(all_films_data, 'movies')

    status, body = await make_get_request('films', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '+imdb_rating', 'page[size]': 2},
                {'status': 200, 'last_rating': 1.0, 'size': 2}
        ),
    ]
)
async def test_all_films_rating(make_get_request, es_write_data, query_data, expected_answer):
    await es_write_data(rating_test_data, 'movies')

    status, body = await make_get_request('films', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']
    assert body[0]['imdb_rating'] == expected_answer['last_rating']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '-imdb_rating', 'page[size]': 50},
                {'status': 200, 'size': 50}
        ),
    ]
)
async def test_all_films_redis(make_get_request, es_write_data, es_del_index, query_data, expected_answer):
    await es_write_data(all_films_data, 'movies')

    status, _ = await make_get_request('films', query_data)

    assert status == expected_answer['status']

    await es_del_index('movies')

    status, body = await make_get_request('films', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'filter[genre]': 'qwerqwer'},
                {'status': 404}
        ),
    ]
)
async def test_all_films(make_get_request, es_write_data, query_data, expected_answer):
    await es_write_data(all_films_data, 'movies')

    status, body = await make_get_request('films', query_data)

    assert status == expected_answer['status']
