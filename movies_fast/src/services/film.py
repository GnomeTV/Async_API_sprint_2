from functools import lru_cache
import logging
from uuid import UUID

from fastapi import Depends

from db.abs_storages import BaseCacheStorage, BaseDbStorage
from db.elastic import get_elastic, ElasticStorage
from db.redis import get_redis, RedisCacheStorage
from models.film import Film
from models.genre import Genre
from models.person import Person


logger = logging.getLogger(__name__)

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, cache_stor: BaseCacheStorage, db_stor: BaseDbStorage):
        self.cache_stor = cache_stor
        self.db_stor = db_stor

    @staticmethod
    def _compile_cache_key(page: int,
                           page_size: int,
                           filter_genre: UUID | None,
                           query: str | None,
                           sort: str,
                           ) -> str:
        return f'page[number]:={page}&' \
               f'page[size]:={page_size}&' \
               f'filter[genre]:={filter_genre}&' \
               f'query:={query}&' \
               f'sort:={sort}'

    @staticmethod
    def _prepare_film_result(film: dict) -> Film:
        genres = []
        for item in film['genre']:
            genres.append(Genre(id=item['id'], name=item['name'], description=''))

        persons = []
        for item in film['actors']:
            persons.append(Person(id=item['id'],
                                  full_name=item['name'],
                                  role='actor'),
                           )
        for item in film['writers']:
            persons.append(Person(id=item['id'],
                                  full_name=item['name'],
                                  role='writer'),
                           )
        for item in film['directors']:
            persons.append(Person(id=item['id'],
                                  full_name=item['name'],
                                  role='director'),
                           )

        return Film(
            id=film['id'],
            file_path=None,
            title=film['title'],
            description=film['description'],
            creation_date=None,
            imdb_rating=film['imdb_rating'],
            type='',
            genres=genres,
            persons=persons,
            created=None,
            modified=None
        )

    async def get_by_id(self, film_id: UUID | None) -> Film | None:
        film = await self.cache_stor.get_object(film_id)
        if not film:
            film = await self.db_stor.get_film(film_id)
            if not film:
                return None
            await self.cache_stor.save_object(film_id, film)
        # преобразовываем в модель
        film = self._prepare_film_result(film)
        return film

    async def get_by_query(self,
                           page: int | None = 1,
                           page_size: int | None = 10,
                           filter_genre: UUID | None = None,
                           query: str | None = None,
                           sort: str = '-imdb_rating') -> list[Film] | None:
        if page is None or page < 1:
            page = 1
        if page_size is None or page_size < 1:
            page_size = 10
        cache_key = self._compile_cache_key(page=page,
                                            page_size=page_size,
                                            filter_genre=filter_genre,
                                            query=query,
                                            sort=sort,
                                            )
        films = await self.cache_stor.get_list_objects(cache_key)
        if not films:
            films = await self.db_stor.search_film(query=query,
                                                   filter_genre=filter_genre,
                                                   offset=page_size * (page - 1),
                                                   limit=page_size,
                                                   sort=sort,
                                                   )
            if not films:
                return None
            await self.cache_stor.save_list_objects(cache_key, films)
        # возвращаем список моделей
        return [self._prepare_film_result(film) for film in films]

# Ниже определяется тип хранилища и кэша, с которыми будет работать FilmService.
# Нужно подготовить и отдать переменные с объектами хранилищ в создаваемый класс.
# При желании можно написать классы для других хранилищ и передавать объекты этих
# классов в создаваемый объект класса FilmService


# объявляем один объект на модуль
redis_cache_film: RedisCacheStorage | None = None
elastic_film: ElasticStorage | None = None


async def get_redis_cache() -> RedisCacheStorage:
    global redis_cache_film
    if redis_cache_film is None:
        redis = await get_redis()
        redis_cache_film = RedisCacheStorage(redis, FILM_CACHE_EXPIRE_IN_SECONDS)
    return redis_cache_film


async def get_elastic_stor() -> ElasticStorage:
    global elastic_film
    if elastic_film is None:
        elastic_conn = await get_elastic()
        elastic_film = ElasticStorage(elastic_conn)
    return elastic_film


@lru_cache()
def get_film_service(
    cache_db: BaseCacheStorage = Depends(get_redis_cache),
    storage_db: BaseDbStorage = Depends(get_elastic_stor),
) -> FilmService:
    return FilmService(cache_db, storage_db)
