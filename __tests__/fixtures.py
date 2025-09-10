from typing import Callable, Coroutine

import pytest

from main import settings
from project.db.models import Database, SessionUserModel


@pytest.fixture
def async_engine():

    def catch():
        db = Database(settings.DATABASE_URL_SQLITE)
        db.init_engine()
        return db

    return catch


@pytest.fixture
def drop_test(async_engine) -> Callable[[], Coroutine]:
    from sqlalchemy import delete

    async def catch() -> None:
        async with async_engine().engine.begin() as conn:
            """Async engine. DELETE the all views/rows in relational db"""
            await conn.execute(delete(SessionUserModel))
            await conn.commit()

    return catch
