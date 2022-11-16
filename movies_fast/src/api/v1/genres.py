from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import Genre, PageParams
from fastapi import APIRouter, Depends, HTTPException, Query
from services.genre import GenreService, get_genre_service

router = APIRouter()

GENRES_404 = "Genre(s) not found"


def get_sq_params(
    page_num: int | None = Query(1, alias="page[number]", ge=1),
    page_size: int | None = Query(10, alias="page[size]", ge=1),
) -> PageParams:
    return PageParams(
        page_num=page_num,
        page_size=page_size,
    )


@router.get(
    "/{genre_id}",
    response_model=Genre,
    summary="Жанр кинопроизведения",
    description="Поиск жанра по id",
    response_description="id и наименование жанра",
    tags=["genres"],
)
async def genre_details(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRES_404)
    return Genre(id=genre.id, name=genre.name)


@router.get(
    "",
    response_model=list[Genre],
    summary="Жанры кинопроизведений",
    description="Список жанров",
    response_description="id и наименование жанра",
    tags=["genres"],
)
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service),
    qp: PageParams = Depends(get_sq_params),
) -> list[Genre]:
    genres = await genre_service.get_genre_list(qp.page_num, qp.page_size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRES_404)
    # преобразовывает ответ сервиса, состоящий из списка моделей бизнес-логики
    # в список моделей апи
    genre_models = []
    for genre in genres:
        genre_models.append(Genre(id=genre.id, name=genre.name))
    return genre_models
