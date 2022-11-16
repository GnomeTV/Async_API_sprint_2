from datetime import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class DateMixin(BaseModel):
    created: datetime | None
    modified: datetime | None
