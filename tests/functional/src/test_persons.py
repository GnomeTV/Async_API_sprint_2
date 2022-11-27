from urllib.parse import urljoin
from http import HTTPStatus

import pytest
import pytest_asyncio
from elasticsearch import NotFoundError

from functional.testdata.es_film_data import films_index_body
from functional.testdata.es_person_data import (
    persons_data,
    persons_index_body,
    pers_film_data,
)


PERSONS_INDEX = "persons"
MOVIES_INDEX = "movies"
HANDLE = "persons"
ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@pytest_asyncio.fixture(scope="module")
async def del_indices(es_client):
    """Удаляет индексы персон и фильмов для чистого старта."""
    for idx in (PERSONS_INDEX, MOVIES_INDEX):
        try:
            await es_client.indices.delete(index=idx)
        except NotFoundError as e:
            print(e)


@pytest_asyncio.fixture()
async def mov_and_pers_idx(es_write_data):
    """Заполняет индексы фильмов и персон."""
    await es_write_data(persons_data, PERSONS_INDEX, persons_index_body)
    await es_write_data(pers_film_data, MOVIES_INDEX, films_index_body)


@pytest.mark.asyncio
async def test_person_by_id(make_get_request, del_indices, mov_and_pers_idx):
    """Тест проверяет, что персона успешно получается по id."""
    pers_id = persons_data[0]["id"]
    status, body = await make_get_request(urljoin(f"{HANDLE}/", pers_id))
    assert status == HTTPStatus.OK
    assert body["id"] == pers_id


@pytest.mark.asyncio
async def test_pers_by_invalid_id(make_get_request, del_indices, mov_and_pers_idx):
    """Тест проверяет ответ с некорректным id.
    Валидация UUID в FastAPI должна вернуть ошибку 422 - UNPROCESSABLE_ENTITY.
    """
    status, body = await make_get_request(f"{HANDLE}/some_wrong_id")
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_pers_by_notfound_id(make_get_request, del_indices, mov_and_pers_idx):
    """Тест проверяет ответ с id, которого нет в индексе."""
    status, body = await make_get_request(f"{HANDLE}/{ZERO_UUID}")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_search_pers(make_get_request, del_indices, mov_and_pers_idx, redis):
    """Тест поиска персоны по имени. В тестовом наборе два Джорджа."""
    # сброс кэша, т.к. при повторных запусках тестов генерятся разные UUID
    # для фильмов и персон, а кэшированная ручка может извлечь старые
    await redis.flushdb()
    status, body = await make_get_request(f"{HANDLE}/search", {"query": "george"})
    assert status == HTTPStatus.OK
    assert len(body) == 2
    georges_ids = {persons_data[0]["id"], persons_data[1]["id"]}
    assert body[0]["id"] in georges_ids
    assert body[1]["id"] in georges_ids


@pytest.mark.asyncio
async def test_search_impossible(make_get_request, del_indices, mov_and_pers_idx):
    """Тест поиска персоны по имени, которого нет."""
    status, body = await make_get_request(f"{HANDLE}/search",
                                          {"query": "Alexander Nevsky"})
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_films_by_pers_id(make_get_request, del_indices, mov_and_pers_idx):
    """Тест проверяет, что по id персоны успешно находятся её фильмы.
    Ищем фильмы Лукаса, в тестовом наборе он в первых двух фильмах.
    """
    pers_id = persons_data[0]["id"]
    status, body = await make_get_request(f"{HANDLE}/{pers_id}/film")
    assert status == HTTPStatus.OK
    assert len(body) == 2
    lucas_film_ids = {pers_film_data[0]["id"], pers_film_data[1]["id"]}
    assert body[0]["id"] in lucas_film_ids
    assert body[1]["id"] in lucas_film_ids


@pytest.mark.asyncio
async def test_films_by_notfound_id(make_get_request, del_indices, mov_and_pers_idx):
    """Тест ищет фильмы несуществующей персоны."""
    status, body = await make_get_request(f"{HANDLE}/{ZERO_UUID}/film")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_pers_id_cache(make_get_request, mov_and_pers_idx, es_del_index):
    """Тест запрашивает персону по id, очищает индекс эластика и делает
    новый запрос. Ожидается, что кэш вернёт идентичный ответ.
    """
    request = urljoin(f"{HANDLE}/", persons_data[-1]["id"])
    status, body_el = await make_get_request(request)
    assert status == HTTPStatus.OK
    await es_del_index(PERSONS_INDEX)
    await es_del_index(MOVIES_INDEX)
    status, body = await make_get_request(request)
    assert status == HTTPStatus.OK
    assert body == body_el


@pytest.mark.asyncio
async def test_person_search_from_cache(make_get_request,
                                        mov_and_pers_idx,
                                        es_del_index,
                                        ):
    """Тест запрашивает поиск персон (с заданной пагинацией), удаляет
    индекс эластика и делает новый запрос. Ответ из кэша должен быть идентичен.
    """
    req_params = {"page[size]": 20,
                  "page[number]": 1,
                  "query": "george"
                  }
    status, body_el = await make_get_request(f"{HANDLE}/search", req_params)
    assert status == HTTPStatus.OK
    await es_del_index(PERSONS_INDEX)
    await es_del_index(MOVIES_INDEX)
    status, body = await make_get_request(f"{HANDLE}/search", req_params)
    assert status == HTTPStatus.OK
    assert body == body_el


@pytest.mark.asyncio
async def test_pers_films_from_cache(make_get_request,
                                        mov_and_pers_idx,
                                        es_del_index,
                                        ):
    """Тест запрашивает фильмы персоны (с заданной пагинацией), удаляет
    индекс эластика и делает новый запрос. Ответ из кэша должен быть идентичен.
    """
    req_params = {"page[size]": 20,
                  "page[number]": 1,
                  }
    pers_id = persons_data[0]["id"]
    status, body_el = await make_get_request(f"{HANDLE}/{pers_id}/film", req_params)
    assert status == HTTPStatus.OK
    await es_del_index(PERSONS_INDEX)
    await es_del_index(MOVIES_INDEX)
    status, body = await make_get_request(f"{HANDLE}/{pers_id}/film", req_params)
    assert status == HTTPStatus.OK
    assert body == body_el
