import json
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError

from db.abs_storages import BaseDbStorage
from db.el_queries import GET_PERSON_FILMS, PERSON_SEARCH_FUZZY

MOVIES_INDEX = "movies"
GENRES_INDEX = "genres"
PERSONS_INDEX = "persons"

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class ElasticStorage(BaseDbStorage):
    """Класс реализует хранилище объектов приложения Фильмы на ElasticSearch."""

    elastic: AsyncElasticsearch

    def __init__(self, elastic_conn: AsyncElasticsearch):
        self.elastic = elastic_conn

    async def get_genre(self, genre_id: UUID) -> dict | None:
        """Получить жанр по id."""
        genre = await self._get_obj_by_id(genre_id, GENRES_INDEX)
        return genre

    async def get_person(self, person_id: UUID) -> dict | None:
        """Получить персону по id."""
        person = await self._get_obj_by_id(person_id, PERSONS_INDEX)
        return person

    async def get_film(self, film_id: UUID) -> dict | None:
        """Получить фильм по id."""
        film = await self._get_obj_by_id(film_id, MOVIES_INDEX)
        return film

    async def get_person_details(self, person_id: UUID) -> dict | None:
        """Получить детали персоны (фильмы, роли) по id."""
        el_query = json.loads(GET_PERSON_FILMS.replace("%pers_id%", str(person_id)))
        try:
            doc = await self.elastic.search(index=MOVIES_INDEX,
                                            body=el_query,
                                            size=100
                                            )
        except NotFoundError:
            return None
        film_ids = set()
        roles = set()
        for item in doc.raw["hits"]["hits"]:
            film_ids.add(item["_id"])
            role_types = ("actors", "writers", "directors")
            for role_type in role_types:
                persons = item["_source"][role_type]
                for pers in persons:
                    if pers["id"] == str(person_id):
                        roles.add(role_type[:-1])  # без "s" в конце
        result = {"role": list(roles), "film_ids": list(film_ids)}
        return result

    async def get_list_genre(
        self,
        offset: int = 0,
        limit: int = 10,
    ) -> list[dict] | None:
        """Получить список жанров - нужное кол-во с нужной позиции."""
        try:
            doc = await self.elastic.search(
                index=GENRES_INDEX,
                from_=offset,
                size=limit,
            )
        except NotFoundError:
            return None
        genres = []
        for item in doc.raw["hits"]["hits"]:
            genres.append(item["_source"])
        return genres

    async def search_person(
        self, query: str, offset: int = 0, limit: int = 10
    ) -> list[dict] | None:
        """Fuzzy search. Возвращает список персон - нужное кол-во с нужной позиции."""
        el_query = json.loads(PERSON_SEARCH_FUZZY.replace("%search_query%", query))
        try:
            doc = await self.elastic.search(
                index=PERSONS_INDEX,
                body=el_query,
                from_=offset,
                size=limit,
            )
        except NotFoundError:
            return None
        return [item["_source"] for item in doc.raw["hits"]["hits"]]

    async def get_pers_films(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> list[dict] | None:
        """Возвращает список фильмов заданной персоны."""
        # строка запроса к индексу фильмов
        el_query = json.loads(GET_PERSON_FILMS.replace("%pers_id%", str(person_id)))
        try:
            doc = await self.elastic.search(
                index=MOVIES_INDEX, body=el_query, from_=offset, size=limit,
            )
        except NotFoundError:
            return None
        films = []
        for item in doc.raw["hits"]["hits"]:
            film = {
                "id": item["_id"],
                "title": item["_source"]["title"],
                "imdb_rating": item["_source"]["imdb_rating"],
            }
            films.append(film)
        return films

    async def search_film(self,
                          query: str | None = None,
                          filter_genre: UUID | None = None,
                          offset: int = 0,
                          limit: int = 10,
                          sort: str = '-imdb_rating',
                          ) -> list[dict] | None:
        """Поиск фильмов с пагинацией и фильтрацией."""
        query_el = self._get_film_query(filter_genre=filter_genre,
                                        offset=offset,
                                        limit=limit,
                                        sort=sort,
                                        query=query,
                                        )
        try:
            doc = await self.elastic.search(index=MOVIES_INDEX, body=query_el)
        except NotFoundError:
            return None
        return [item["_source"] for item in doc.raw["hits"]["hits"]]

    async def _get_obj_by_id(self, obj_id: UUID, index_name: str) -> dict | None:
        """Возвращает элемент указанного индекса по id."""
        try:
            doc = await self.elastic.get(index=index_name, id=str(obj_id))
        except NotFoundError:
            return None
        return doc["_source"]

    @staticmethod
    def _get_film_query(filter_genre: UUID | None = None,
                        offset: int = 0,
                        limit: int = 10,
                        query: str | None = None,
                        sort: str = '-imdb_rating',
                        ) -> dict:
        query_result = {
            "size": limit,
            "from": offset,
            "sort": [
                {
                    "imdb_rating": {
                        "order": "desc"
                    }
                }
            ]
        }
        if filter_genre:
            query_result["query"] = {
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

        if query_result.get("query") and query:
            query_result["query"]["bool"].update({
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
            query_result["query"] = {
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

        if sort == "+imdb_rating":
            query_result["sort"][0]["imdb_rating"]["order"] = "asc"

        return query_result
