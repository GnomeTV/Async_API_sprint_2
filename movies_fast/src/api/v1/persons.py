from http import HTTPStatus
from uuid import UUID

from api.v1.schemas import MovieShortInfo, PageParams, PersonInfo
from fastapi import APIRouter, Depends, HTTPException, Query
from services.person import PersonService, get_person_service

router = APIRouter()

PERSON_404 = "Person(s) not found"
PERSON_FILMS_404 = "Films for person not found"


def get_pg_params(
    page_num: int | None = Query(1, alias="page[number]", ge=1),
    page_size: int | None = Query(10, alias="page[size]", ge=1),
) -> PageParams:
    return PageParams(
        page_num=page_num,
        page_size=page_size,
    )


@router.get(
    "/search",
    response_model=list[PersonInfo],
    summary="Поиск по персонам",
    description="Поиск персоны по частичному совпадению имени",
    response_description="id, имя персоны, список ролей и фильмов",
    tags=["persons"],
)
async def person_search(
    person_service: PersonService = Depends(get_person_service),
    qp: PageParams = Depends(get_pg_params),
    query: str = Query(""),
) -> list[PersonInfo]:
    persons = await person_service.search_person(query, qp.page_num, qp.page_size)
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PERSON_404,
        )
    # преобразовывает ответ сервиса, состоящий из списка моделей бизнес-логики
    # в список моделей апи
    return [PersonInfo(**person) for person in persons]


@router.get(
    "/{person_id}/film",
    response_model=list[MovieShortInfo],
    summary="Фильмы персоны",
    description="Список фильмов по персоне",
    response_description="id, название и рейтинг фильма",
    tags=["persons"],
)
async def person_films(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    qp: PageParams = Depends(get_pg_params),
) -> list[MovieShortInfo]:
    films = await person_service.get_pers_films(person_id, qp.page_num, qp.page_size)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PERSON_FILMS_404,
        )
    return [MovieShortInfo(**film) for film in films]


@router.get(
    "/{person_id}",
    response_model=PersonInfo,
    summary="Информация по персоне",
    description="Поиск персоны по id",
    response_description="id, имя персоны, список ролей и фильмов",
    tags=["persons"],
)
async def person_details(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonInfo:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_404)
    return PersonInfo(**person)
