import os
from typing import Optional, List
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
)


# SETTING
class Settings(BaseSettings):
    SQLITE_DB_PATH: str = (os.path.join(BASE_DIR, "truckdriver_db.sqlite3")).replace(
        "\\", "/"
    )
    SECRET_KEY = uuid7()
    POSTGRES_PORT: str = POSTGRES_PORT
    POSTGRES_DB: str = POSTGRES_DB
    POSTGRES_PASSWORD: str = POSTGRES_PASSWORD
    POSTGRES_USER: str = POSTGRES_USER
    POSTGRES_HOST: str = POSTGRES_HOST
    ALLOWED_ORIGINS: List[str] = ["127.0.0.1", "83.166.245.209"]
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
    CSRF_COOKIE_HTTPONLY: bool = False
    CSRF_COOKIE_SAMESITE: str = "lax"
    CSRF_COOKIE_SECURE: bool = not DEBUG

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
            )
        )

        exists = result.scalar()
        if exists == 0:
            await conn.close()
            # await conn.execute(text("""CREATE DATABASE %s"""),[name_db])
            async with engine.begin() as conn:
                await conn.run_sync(meta.create_all)
