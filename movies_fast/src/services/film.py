import json
import logging
from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from aioredis.exceptions import ConnectionError
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film
from models.genre import Genre
from models.person import Person

logger = logging.getLogger(__name__)

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @staticmethod
    async def get_elastic_query(filter_genre: Optional[UUID] = None,
                                page: int = 0,
                                page_size: int = 10,
                                query: Optional[str] = None,
                                sort: str = '-imdb_rating') -> dict:
        query_result = {
            "size": page_size,
            "from": page,
            "sort": [
                {
                    "imdb_rating": {
                        "order": "desc"
                    }
                }
            ]
        }
        if filter_genre:
            query_result['query'] = {
                "bool": {
                    "filter": {
                        "nested": {
                            "path": "genre",
                            "query": {
                                "term": {
                                    "genre.id": f"{filter_genre}"
                                }
                            }
                        }
                    }
                }
            }

        if query_result.get('query') and query:
            query_result['query']['bool'].update({
                "must": {
                    "fuzzy": {
                        "title": {
                            "value": f"{query}",
                            "fuzziness": "AUTO"
                        }
                    }
                }
            })
        elif query:
            query_result['query'] = {
                "bool": {
                    "must": {
                        "fuzzy": {
                            "title": {
                                "value": f"{query}",
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                }
            }

        if sort == '+imdb_rating':
            query_result['sort'][0]['imdb_rating']['order'] = "asc"

        return query_result

    @staticmethod
    async def _compile_redis_key(page: int, page_size: int, filter_genre: Optional[UUID], query: Optional[str],
                                 sort: str) -> str:
        return f'page[number]:={page}&' \
               f'page[size]:={page_size}&' \
               f'filter[genre]:={filter_genre}&' \
               f'query:={query}&' \
               f'sort:={sort}'

    @staticmethod
    async def _prepare_film_result(film: dict) -> Film:
        genres = []
        for item in film['genre']:
            genres.append(Genre(id=item['id'], name=item['name'], description=''))

        persons = []
        for item in film['actors']:
            persons.append(Person(id=item['id'], full_name=item['name'], role='actor'))
        for item in film['writers']:
            persons.append(Person(id=item['id'], full_name=item['name'], role='writer'))
        for item in film['directors']:
            persons.append(Person(id=item['id'], full_name=item['name'], role='director'))

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

    async def get_by_id(self, film_id: Optional[str]) -> Optional[Film]:
        try:
            film = await self._film_from_cache(film_id)
        except ConnectionError as e:
            film = None
            logger.error(e)

        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None

            await self._put_film_to_cache(film)

        return film

    async def get_by_query(self,
                           page: Optional[int],
                           page_size: Optional[int],
                           filter_genre: Optional[UUID],
                           query: Optional[str],
                           sort: str = '-imdb_rating') -> Optional[list[Film]]:
        try:
            films = await self._film_list_from_cache(page=page, page_size=page_size, filter_genre=filter_genre,
                                                     query=query, sort=sort)
        except ConnectionError as e:
            films = None
            logger.error(e)

        if not films:
            films = await self._get_film_list_from_elastic(filter_genre=filter_genre, page_size=page_size,
                                                           page=page, query=query, sort=sort)
            if not films:
                return None

            await self._put_film_list_to_cache(page=page, page_size=page_size, filer_genre=filter_genre, sort=sort,
                                               films=films, query=query)

        return films

    async def _get_film_list_from_elastic(self,
                                          query: Optional[str],
                                          filter_genre: Optional[UUID],
                                          page: int = 0,
                                          page_size: int = 10,
                                          sort: str = '-imdb_rating') -> Optional[list[Film]]:
        try:
            query = await self.get_elastic_query(filter_genre=filter_genre, page_size=page_size, page=page, sort=sort,
                                                 query=query)
            doc = await self.elastic.search(index="movies", body=query)
        except NotFoundError:
            return None
        films = []
        for item in doc['hits']['hits']:
            film = await self._prepare_film_result(item['_source'])
            films.append(film)
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        film = doc["_source"]
        return await self._prepare_film_result(film)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _film_list_from_cache(self,
                                    page: int,
                                    page_size: int,
                                    filter_genre: UUID,
                                    query: Optional[str],
                                    sort: str = '-imdb_rating') -> Optional[list[Film]]:
        key = await self._compile_redis_key(page=page, page_size=page_size, filter_genre=filter_genre, query=query,
                                            sort=sort)
        data = await self.redis.get(key)
        if not data:
            return None
        data = json.loads(data)
        films = []
        for item in data:
            films.append(Film.parse_raw(item))

        return films

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(str(film.id), film.json())

    async def _put_film_list_to_cache(self,
                                      page: int,
                                      page_size: int,
                                      filer_genre: Optional[UUID],
                                      query: Optional[str],
                                      sort: str,
                                      films: Optional[list[Film]]):
        key = await self._compile_redis_key(page=page, page_size=page_size, filter_genre=filer_genre, query=query,
                                            sort=sort)
        films_json = [film.json() for film in films]
        await self.redis.set(key, json.dumps(films_json))


@lru_cache()
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticsearch = Depends(get_elastic), ) -> FilmService:
    return FilmService(redis, elastic)
