import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.abs_storages import BaseCacheStorage, BaseDbStorage
from db.elastic import get_elastic, ElasticStorage
from db.redis import get_redis, RedisCacheStorage

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, cache_stor: BaseCacheStorage, db_stor: BaseDbStorage):
        self.cache_stor = cache_stor
        self.db_stor = db_stor

    async def get_by_id(self, person_id: UUID) -> dict | None:
        """Возвращает персону по id."""
        person = await self.cache_stor.get_object(person_id)
        if person:
            logging.debug("Person cache hit - %s", person["name"])
        if not person:
            # нет в кеше - ищем в базе
            # 1 часть словаря: id и name
            person = await self.db_stor.get_person(person_id)
            if not person:
                return None
            # вытаскиваем детали по персоне: роли и фильмы (2 часть словаря)
            person_det = await self._get_person_details(person_id)
            # объединяем словари
            person = person | person_det
            # Сохраняем персону в кеш
            await self.cache_stor.save_object(person_id, person)
            logging.debug("Person saved to cache - %s", person["name"])
        return person

    @staticmethod
    def _get_cache_key(prefix: str, page: int, size: int) -> str:
        return f"{prefix}_page:{page}_size:{size}"

    async def _get_person_details(self, person_id: UUID) -> dict | None:
        """Возвращает роли и фильмы запрошенной персоны.

        Используется как при запросе "одиночной" ручки, так и ручки поиска персон.
        """
        # проверяем кэш: может отдельная ручка запрашивала детали этой персоны
        person_det = await self.cache_stor.get_object(person_id)
        if person_det:
            logging.debug("Person details cache hit - %s", person_id)
        # не нашли в кэше - ищем в базе
        if not person_det:
            person_det = await self.db_stor.get_person_details(person_id)
        return person_det

    async def search_person(
        self,
        query: str,
        page: int | None = 1,
        size: int | None = 10,
    ) -> list[dict] | None:
        """Ищет персон и выдаёт список подходящих."""
        if page is None or page < 1:
            page = 1
        if size is None or size < 1:
            size = 10
        cache_key = self._get_cache_key(f"persons({query})", page, size)
        # ищем в кеше по ключу
        persons = await self.cache_stor.get_list_objects(cache_key)
        if persons:
            logging.debug("Person search cache hit - %s", cache_key)
        if not persons:
            # в кеше не найдено - ищем в базе
            p_list = await self.db_stor.search_person(
                query, size * (page - 1), size,
            )
            if not p_list:
                return None
            # запрашиваем детали по каждой персоне, они могут тянуться
            # как из кэша, так и из базы
            persons = []
            for person in p_list:
                pers_id = UUID(person["id"])
                pers_det = await self._get_person_details(pers_id)
                # слияние словарей id-name + детали
                full_pers = person | pers_det
                # сохраняем в кэш отдельную запись персоны
                await self.cache_stor.save_object(pers_id, full_pers)
                logging.debug("Person saved to cache - %s", person["name"])
                # добавляем в итоговый список
                persons.append(full_pers)
            # сохраняем в кэш весь ответ ручки
            await self.cache_stor.save_list_objects(cache_key, persons)
            logging.debug("Genre list saved to cache - %s", cache_key)
        return persons

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
        cache_key = self._get_cache_key(f"pers_films({str(person_id)})", page, size)
        # ищем в кеше по ключу
        films = await self.cache_stor.get_list_objects(cache_key)
        if films:
            logging.debug("Person films cache hit - %s", cache_key)
        if not films:
            films = await self.db_stor.get_pers_films(
                person_id, size * (page - 1), size,
            )
            if not films:
                return None
            # сохраняем в кэш ответ ручки
            await self.cache_stor.save_list_objects(cache_key, films)
            logging.debug("Person films saved to cache - %s", cache_key)
        return films

# Ниже определяется тип хранилища и кэша, с которыми будет работать PersonService.
# Нужно подготовить и отдать переменные с объектами хранилищ в создаваемый класс.
# При желании можно написать классы для других хранилищ и передавать объекты этих
# классов в создаваемый объект класса PersonService


# объявляем один объект на модуль
redis_cache_genre: RedisCacheStorage | None = None
elastic_genre: ElasticStorage | None = None


async def get_redis_cache() -> RedisCacheStorage:
    global redis_cache_genre
    if redis_cache_genre is None:
        redis = await get_redis()
        redis_cache_genre = RedisCacheStorage(redis, PERSON_CACHE_EXPIRE_IN_SECONDS)
    return redis_cache_genre


async def get_elastic_stor() -> ElasticStorage:
    global elastic_genre
    if elastic_genre is None:
        elastic_conn = await get_elastic()
        elastic_genre = ElasticStorage(elastic_conn)
    return elastic_genre


@lru_cache()
def get_person_service(
    cache_db: BaseCacheStorage = Depends(get_redis_cache),
    storage_db: BaseDbStorage = Depends(get_elastic_stor),
) -> PersonService:
    return PersonService(cache_db, storage_db)
