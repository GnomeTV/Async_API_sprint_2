import pytest

from functional.testdata.es_film_data import rating_test_data, search_star_data, genre_id, search_star_genre_data

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '-imdb_rating', 'page[size]': 3, 'query': 'star'},
                {'status': 200, 'size': 2}
        ),
    ]
)
async def test_search_star_films(make_get_request, es_del_index, es_write_data, query_data, expected_answer):
    await es_del_index('movies')
    await es_write_data(search_star_data, 'movies')

    status, body = await make_get_request('films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '+imdb_rating', 'page[size]': 3, 'query': 'star'},
                {'status': 200, 'min_rating': 1.0, 'size': 2}
        ),
    ]
)
async def test_search_rating_films(make_get_request, es_del_index, es_write_data, query_data, expected_answer):
    await es_del_index('movies')
    await es_write_data(rating_test_data, 'movies')

    status, body = await make_get_request('films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']
    assert body[0]['imdb_rating'] == expected_answer['min_rating']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '-imdb_rating', 'filter[genre]': genre_id, 'query': 'star'},
                {'status': 200, 'size': 2}
        ),
    ]
)
async def test_search_film_genre(make_get_request, es_write_data, es_del_index, query_data, expected_answer):
    await es_del_index('movies')
    await es_write_data(search_star_genre_data, 'movies')

    status, body = await make_get_request('films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'sort': '-imdb_rating', 'filter[genre]': genre_id, 'query': 'star'},
                {'status': 200, 'size': 2}
        ),
    ]
)
async def test_search_film_genre_redis(make_get_request, es_write_data, es_del_index, query_data, expected_answer):
    await es_del_index('movies')
    await es_write_data(search_star_genre_data, 'movies')
    await es_del_index('movies')

    status, body = await make_get_request('films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['size']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'oqwieuryqowieuryqowieury'},
                {'status': 404}
        ),
    ]
)
async def test_search_film_error(make_get_request, es_write_data, es_del_index, query_data, expected_answer):
    await es_del_index('movies')
    await es_write_data(search_star_genre_data, 'movies')

    status, _ = await make_get_request('films/search', query_data)

    assert status == expected_answer['status']
