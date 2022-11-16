import json
import logging
from functools import lru_cache
from uuid import UUID

from aioredis import Redis
from db.el_queries import GET_PERSON_FILMS, PERSON_SEARCH_FUZZY
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> dict | None:
        """Возвращает персону по id."""
        person = await self._person_from_cache(person_id)
        if person:
            logging.debug("Person cache hit - %s", person["name"])
        if not person:
            # нет в кеше - ищем его в Elasticsearch
            # 1 часть словаря: id и name
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            # вытаскиваем детали по персоне: роли и фильмы (2 часть словаря)
            person_det = await self._get_person_details(person_id)
            # объединяем словари
            person = person | person_det
            # Сохраняем персону в кеш
            await self._put_person_to_cache(person_id, person)
            logging.debug("Person saved to cache - %s", person["name"])
        return person

    @staticmethod
    def _get_redis_key(prefix: str, page: int, size: int) -> str:
        return f"{prefix}_page:{page}_size:{size}"

    async def _get_person_details(self, person_id: UUID) -> dict | None:
        """Возвращает роли и фильмы запрошенной персоны.

        Используется как при запросе "одиночной" ручки, так и ручки поиска персон.
        """
        # проверяем кэш: может отдельная ручка запрашивала детали этой персоны
        person_det = await self._person_from_cache(person_id)
        if person_det:
            logging.debug("Person details cache hit - %s", person_id)
        # не нашли в кэше - ищем в эластике
        if not person_det:
            person_det = await self._get_person_det_from_elastic(person_id)
        return person_det

    async def _get_person_det_from_elastic(self, person_id: UUID) -> dict | None:
        # строка запроса к индексу фильмов
        el_query = json.loads(GET_PERSON_FILMS.replace("%pers_id%", str(person_id)))
        try:
            doc = await self.elastic.search(index="movies", body=el_query, size=100)
        except NotFoundError:
            return None
        film_ids = set()
        roles = set()
        for item in doc.raw["hits"]["hits"]:
            # забираем id фильма в список
            film_ids.add(item["_id"])
            # перебираем словари с актёрами, сценаристами и режиссёрами
            # и ищем, кем была запрошенная персона
            role_types = ("actors", "writers", "directors")
            for role_type in role_types:
                persons = item["_source"][role_type]
                for pers in persons:
                    if pers["id"] == str(person_id):
                        roles.add(role_type[:-1])  # без "s" в конце
        result = {"role": list(roles), "film_ids": list(film_ids)}
        return result

    async def _get_person_from_elastic(self, person_id: UUID) -> dict | None:
        # просто находим персону по id в индексе persons (одиночная ручка)
        try:
            doc = await self.elastic.get(index="persons", id=str(person_id))
        except NotFoundError:
            return None
        person = doc["_source"]
        return person

    async def _person_from_cache(self, person_id: UUID) -> dict | None:
        data = await self.redis.get(f"person_{str(person_id)}")
        if not data:
            return None
        return json.loads(data)

    async def _put_person_to_cache(self, person_id: UUID, person: dict):
        await self.redis.set(
            f"person_{str(person_id)}",
            json.dumps(person),
            ex=PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_person_list(
        self,
        query: str,
        page: int | None = 1,
        size: int | None = 10,
    ) -> list[dict] | None:
        """Ищет персон по частичному совпадению имени (fuzzy search)."""
        if page is None or page < 1:
            page = 1
        if size is None or size < 1:
            size = 10
        redis_key = self._get_redis_key(f"persons({query})", page, size)
        # ищем в кеше по ключу
        persons = await self._list_from_cache(redis_key)
        if persons:
            logging.debug("Person search cache hit - %s", redis_key)
        if not persons:
            # в кеше не найдено - ищем в эластике
            p_list = await self._get_person_list_from_elastic(
                query, size * (page - 1), size,
            )
            if not p_list:
                return None
            # запрашиваем детали по каждой персоне, они могут тянуться
            # как из кэша, так и эластика
            persons = []
            for person in p_list:
                pers_id = UUID(person["id"])
                pers_det = await self._get_person_details(pers_id)
                # слияние словарей id-name + детали
                full_pers = person | pers_det
                # сохраняем в кэш отдельную запись персоны
                await self._put_person_to_cache(pers_id, full_pers)
                logging.debug("Person saved to cache - %s", person["name"])
                # добавляем в итоговый список
                persons.append(full_pers)
            # сохраняем в кэш весь ответ ручки
            await self._put_list_to_cache(redis_key, persons)
            logging.debug("Genre list saved to cache - %s", redis_key)
        return persons

    async def _get_person_list_from_elastic(
        self,
        query: str,
        offset: int,
        limit: int,
    ) -> list[dict] | None:
        """Возвращает из эластика список персон id, name."""
        el_query = json.loads(PERSON_SEARCH_FUZZY.replace("%search_query%", query))
        try:
            doc = await self.elastic.search(
                index="persons",
                body=el_query,
                from_=offset,
                size=limit,
            )
        except NotFoundError:
            return None
        persons = []
        for item in doc.raw["hits"]["hits"]:
            persons.append(item["_source"])
        return persons

    async def _list_from_cache(self, redis_key: str) -> list[dict] | None:
        data = await self.redis.get(redis_key)
        if not data:
            return None
        return list(json.loads(data))

    async def _put_list_to_cache(self, redis_key: str, items: list[dict]):
        await self.redis.set(
            redis_key,
            json.dumps(items),
            ex=PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_pers_films(
        self,
        person_id: UUID,
        page: int | None = 1,
        size: int | None = 10,
    ) -> list[dict] | None:
        """Выдаёт список фильмов по запрошенной персоне."""
        if page is None or page < 1:
            page = 1
        if size is None or size < 1:
            size = 10
        redis_key = self._get_redis_key(f"pers_films({str(person_id)})", page, size)
        # ищем в кеше по ключу
        films = await self._list_from_cache(redis_key)
        if films:
            logging.debug("Person films cache hit - %s", redis_key)
        if not films:
            # в кеше не найдено - ищем в эластике
            films = await self._get_pers_films_from_elastic(
                person_id, size * (page - 1), size,
            )
            if not films:
                return None
            # сохраняем в кэш ответ ручки
            await self._put_list_to_cache(redis_key, films)
            logging.debug("Person films saved to cache - %s", redis_key)
        return films

    async def _get_pers_films_from_elastic(
        self,
        person_id: UUID,
        offset: int,
        limit: int,
    ) -> list[dict] | None:
        # строка запроса к индексу фильмов
        el_query = json.loads(GET_PERSON_FILMS.replace("%pers_id%", str(person_id)))
        try:
            doc = await self.elastic.search(
                index="movies", body=el_query, from_=offset, size=limit,
            )
        except NotFoundError:
            return None
        # собираем фильмы персонажа в список
        films = []
        for item in doc.raw["hits"]["hits"]:
            # id фильма
            film = {
                "id": item["_id"],
                "title": item["_source"]["title"],
                "imdb_rating": item["_source"]["imdb_rating"],
            }
            films.append(film)
        return films


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
