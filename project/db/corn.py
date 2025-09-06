import os
from typing import Optional, List

from jinja2 import PrefixLoader
from pydantic.v1 import BaseSettings
from starlette.templating import Jinja2Templates
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
    SQLITE_DB_PATH: str = (os.path.join(BASE_DIR, "truckdriver_db.sqlite3")).replace(
        "\\", "/"
    )
    SECRET_KEY = str(uuid7())
    POSTGRES_PORT: str = POSTGRES_PORT
    POSTGRES_DB: str = POSTGRES_DB
    POSTGRES_PASSWORD: str = POSTGRES_PASSWORD
    POSTGRES_USER: str = POSTGRES_USER
    POSTGRES_HOST: str = POSTGRES_HOST
    ALLOWED_ORIGINS: List[str] = [
        f"http://{APP_HOST}",
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
    CSRF_COOKIE_HTTPONLY: bool = False
    CSRF_COOKIE_SAMESITE: str = "lax"
    CSRF_COOKIE_SECURE: bool = not DEBUG
    CSRF_COOKIE_MAX_AGE: int = 20

    @property
    def DATABASE_URL_PS(self) -> str:
        # POSTGRES
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SQLITE(self) -> str:
        # SQLIte
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"


async def create_db(settings: Settings()):
    from sqlalchemy import text, MetaData
    from sqlalchemy.ext.asyncio import create_async_engine

    meta = MetaData()
    engine = create_async_engine(settings.DATABASE_URL_SQLITE, echo=True)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """SELECT %s FROM sqlite_master WHERE name ='%s';"""
                % (1, settings.POSTGRES_DB)
            ),
        )

        exists = result.scalar()
        if exists == 0:
            await conn.close()
            # await conn.execute(text("""CREATE DATABASE %s"""),[name_db])
            async with engine.begin() as conn:
                await conn.run_sync(meta.create_all)
