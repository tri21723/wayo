from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from app.errors import api_error
from app.settings import get_settings


@lru_cache(maxsize=4)
def engine_for(url: str) -> Engine:
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":
        engine = engine.execution_options(schema_translate_map={"wayo": None})

        @event.listens_for(engine, "connect")
        def foreign_keys(dbapi_connection, _connection_record):
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


def get_session() -> Generator[Session, None, None]:
    url = get_settings().database_url
    if not url:
        raise api_error(
            503, "DATABASE_NOT_CONFIGURED", "Tính năng lưu chuyến đi chưa được cấu hình."
        )
    with Session(engine_for(url)) as session:
        yield session


Database = Annotated[Session, Depends(get_session)]
