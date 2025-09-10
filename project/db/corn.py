"""
project/db/corn.py
"""

import os
from typing import List
from pydantic.v1 import BaseSettings
from uuid_extensions import uuid7
from dotenv_ import (
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    POSTGRES_HOST,
    BASE_DIR,
    DEBUG,
    APP_HOST,
    APP_PORT,
    DATABASE_ENGINE_REMOTE,
)

# TEMPLATE


# SETTING
class Settings(BaseSettings):
    SECRET_KEY = str(uuid7())
    SESSIONS_LIVE_TIME: int = 60 * 60  # of seconds
    # SQLITE
    SQLITE_DB_PATH: str = (
        os.path.join(BASE_DIR, "%s_db.sqlite3" % POSTGRES_DB)
    ).replace("\\", "/")
    # POSTGRES
    POSTGRES_PORT: str = POSTGRES_PORT
    POSTGRES_DB: str = POSTGRES_DB
    POSTGRES_PASSWORD: str = POSTGRES_PASSWORD
    POSTGRES_USER: str = POSTGRES_USER
    POSTGRES_HOST: str = POSTGRES_HOST
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        f"http://{APP_HOST}:{int(APP_PORT)}",
        f"http://{DATABASE_ENGINE_REMOTE}",
        "http://0.0.0.0:8000",
    ]
    ALLOWED_ORIGIN_REGEX: List[str] = [
        f"http://{APP_HOST}",
        f"http://{APP_HOST}:{int(APP_PORT)}",
        f"http://{DATABASE_ENGINE_REMOTE}",
        "http://0.0.0.0:8000",
    ]
    ALLOWED_METHODS: List[str] = [
        "HEAD",
        "OPTIONS",
        "TRACE",
        "GET",
        "PUT",
        "DELETE",
        "PATCH",
        "POST",
    ]
    ALLOWED_HEADERS: List[str] = [
        "accept",
        "accept-encoding",
        "Authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "Accept-Language",
        "Content-Language",
    ]
    TEMPLATES_DIR: str = (os.path.join(BASE_DIR, "truckdriver_db.sqlite3")).replace(
        "\\", "/"
    )
    # CSRF COOKIE
    CSRF_COOKIE_HTTPONLY: bool = False
    CSRF_COOKIE_SAMESITE: str = "lax"
    CSRF_COOKIE_SECURE: bool = not DEBUG
    CSRF_COOKIE_MAX_AGE: int = 40

    @property
    def DATABASE_URL_PS(self) -> str:
        # POSTGRES
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SQLITE(self) -> str:
        # SQLIte sqlite+aiosqlite
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"


# УДАЛИТЬ
async def create_db(settings: Settings()):
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(settings.DATABASE_URL_SQLITE, echo=True)
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""SELECT %s FROM sqlite_master WHERE name =%s;""" % (1, "tbl_name")),
        )
