from urllib.parse import urljoin
from http import HTTPStatus

import pytest
import pytest_asyncio
from elasticsearch import NotFoundError

from functional.testdata.es_genre_data import genres_data, genres_index_body

GENRES_INDEX = "genres"
HANDLE = "genres"
ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@pytest_asyncio.fixture(scope="module")
async def del_genres_idx(es_client):
    try:
        await es_client.indices.delete(index=GENRES_INDEX)
    except NotFoundError as e:
        print(e)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"genre_id": genres_data[-1]["id"]},
                {"status": HTTPStatus.OK, "id": genres_data[-1]["id"]}
        ),
    ]
)
@pytest.mark.asyncio
async def test_genre_by_id(make_get_request,
                           es_write_data,
                           query_data,
                           expected_answer,
                           del_genres_idx,
                           ):
    """Тест проверяет, что жанр успешно получается по id."""
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    status, body = await make_get_request(urljoin(f"{HANDLE}/", query_data["genre_id"]))
    assert status == expected_answer["status"]
    assert body["id"] == expected_answer["id"]


@pytest.mark.asyncio
async def test_genre_by_invalid_id(make_get_request, es_write_data, del_genres_idx):
    """Тест проверяет ответ с некорректным id.
    Валидация UUID в FastAPI должна вернуть ошибку 422 - UNPROCESSABLE_ENTITY.
    """
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    status, body = await make_get_request(f"{HANDLE}/some_wrong_id")
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_by_notfound_id(make_get_request, es_write_data, del_genres_idx):
    """Тест проверяет ответ с id, которого нет в индексе."""
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    status, body = await make_get_request(f"{HANDLE}/{ZERO_UUID}")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_all_genres(make_get_request, es_write_data, del_genres_idx):
    """Тест проверяет, что вернутся все тестовые жанры.
    Предполагается, что в тестовом наборе их меньше запрошенных 50 на страницу.
    """
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    status, body = await make_get_request(HANDLE, {'page[size]': 50})
    assert status == HTTPStatus.OK
    assert len(body) == len(genres_data)


@pytest.mark.asyncio
async def test_genres_pagination(make_get_request, es_write_data, del_genres_idx):
    """Тест проверяет, что вернётся страница с запрошенным размером."""
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    page_size = 10
    status, body = await make_get_request(HANDLE,
                                          {"page[size]": page_size,
                                           "page[number]": 1
                                           }
                                          )
    assert status == HTTPStatus.OK
    assert len(body) == page_size


@pytest.mark.asyncio
async def test_genre_id_cache(make_get_request, es_write_data, es_del_index):
    """Тест запрашивает жанр по id, очищает индекс эластика и делает
    новый запрос. Ожидается, что кэш вернёт идентичный ответ.
    """
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    request = urljoin(f"{HANDLE}/", genres_data[-1]["id"])
    status, _ = await make_get_request(request)
    assert status == HTTPStatus.OK
    await es_del_index(GENRES_INDEX)
    status, body = await make_get_request(request)
    assert status == HTTPStatus.OK
    assert body["id"] == genres_data[-1]["id"]


@pytest.mark.asyncio
async def test_genre_list_from_cache(make_get_request, es_write_data, es_del_index):
    """Тест запрашивает определённую страницу (по номеру и размеру), удаляет
    индекс эластика и делает новый запрос. Ответ из кэша должен быть идентичен.
    """
    await es_write_data(genres_data, GENRES_INDEX, genres_index_body)
    req_params = {"page[size]": 3,
                  "page[number]": 2
                  }
    status, body_el = await make_get_request(HANDLE, req_params)
    assert status == HTTPStatus.OK
    await es_del_index(GENRES_INDEX)
    status, body = await make_get_request(HANDLE, req_params)
    assert status == HTTPStatus.OK
    assert body == body_el
