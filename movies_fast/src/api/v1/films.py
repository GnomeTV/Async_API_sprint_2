from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import Film, SquareBracketsParams
from fastapi import APIRouter, Depends, HTTPException, Query
from services.film import FilmService, get_film_service

router = APIRouter()

FILMS_404 = "Film(s) not found"


def get_sq_params(
        page_num: int | None = Query(0, alias="page[number]", ge=0),
        page_size: int | None = Query(10, alias="page[size]", ge=1),
        filter_genre: str | None = Query(None, alias="filter[genre]"),
) -> SquareBracketsParams:
    return SquareBracketsParams(page_num=page_num, page_size=page_size, filter_genre=filter_genre)


async def prepare_film_result(film) -> Film:
    genres = []
    for item in film.genres:
        genres.append(item.dict(exclude={'description', 'created', 'modified'}))

    persons = {
        'actor': [],
        'writer': [],
        'director': []
    }
    writes_names = []
    actors_names = []
    directors_names = []
    for item in film.persons:
        persons[item.role].append({'id': item.id, 'name': item.full_name})
        if item.role == 'actor':
            actors_names.append(item.full_name)
        if item.role == 'writer':
            writes_names.append(item.full_name)
        if item.role == 'director':
            directors_names.append(item.full_name)

    return Film(
        id=film.id,
        imdb_rating=film.imdb_rating,
        genre=genres,
        title=film.title,
        description=film.description,
        director=directors_names,
        actors_names=actors_names,
        writers_names=writes_names,
        actors=persons['actor'],
        writers=persons['writer'],
        directors=persons['director']
    )


@router.get("/search",
            response_model=list[Film],
            summary='Поиск кинопроизведений',
            description='Поиск кинопроизведений по слову в названии',
            response_description='Список кинопроизведений с названием, рейтингом, жанрами, актерами, '
                                 'сценаристами и режиссерами',
            tags=['Полнотекстовый поиск'])
async def list_films_query(query: str | None,
                     film_service: FilmService = Depends(get_film_service),
                     qp: SquareBracketsParams = Depends(get_sq_params),
                     sort: str = "-imdb_rating") -> list[Film]:
    films = await film_service.get_by_query(page=qp.page_num, page_size=qp.page_size, filter_genre=qp.filter_genre,
                                            sort=sort, query=query)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILMS_404)

    result = []
    for item in films:
        result.append(await prepare_film_result(item))

    return result


@router.get("/{film_id}",
            response_model=Film,
            summary='Поиск кинопроизведений',
            description='Поиск кинопроизведений по id',
            response_description='Кинопроизведение с названием, рейтингом, жанрами, актерами, '
                                 'сценаристами и режиссерами',
            tags=['Полнотекстовый поиск'])
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service), ) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILMS_404)

    return await prepare_film_result(film)


@router.get("",
            response_model=list[Film],
            summary='Поиск кинопроизведений',
            description='Поиск кинопроизведений с пагинацией',
            response_description='Кинопроизведение с названием, рейтингом, жанрами, актерами, '
                                 'сценаристами и режиссерами',
            tags=['Полнотекстовый поиск'])
async def list_films(film_service: FilmService = Depends(get_film_service),
                     qp: SquareBracketsParams = Depends(get_sq_params),
                     sort: str = "-imdb_rating") -> list[Film]:
    films = await film_service.get_by_query(page=qp.page_num, page_size=qp.page_size, filter_genre=qp.filter_genre,
                                            sort=sort, query=None)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILMS_404)

    result = []
    for item in films:
        result.append(await prepare_film_result(item))

    return result
