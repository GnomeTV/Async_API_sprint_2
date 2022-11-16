import logging

import aioredis
from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=settings.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf-8",
        decode_responses=True,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"http://{settings.elastic_host}:{settings.elastic_port}"],
    )


@app.on_event("shutdown")
async def shutdown():
    # aioredis в версии библиотеки 2.х сам закрывает соединения при сборке
    # мусора, т.е. когда redis.redis будет удалена
    await elastic.es.close()


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    logging.critical("Do not run module directly, use uvicorn/Gunicorn")
    logging.info("example: uvicorn main:app --host 0.0.0.0 --port 8000")
