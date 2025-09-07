import asyncio
import logging
import re
from typing import List

from pydantic import BaseModel, ConfigDict

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ColumnElement,
    create_engine,
    inspect,
)
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, Mapped
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

Base = declarative_base()


class BaseSession(BaseModel):
    session_id: int = None
    created_at: ColumnElement[DateTime] = None
    expires_at: ColumnElement[DateTime] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class SessionUserModel(Base):
    """
    FOr a work to the user's session
    """

    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        "session",
        String,
        unique=True,
        nullable=False,
        comment="Session ID for anyone of user",
    )
    created_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime, default=lambda: datetime.now() + timedelta(hours=1))

    @property
    def is_expired(self) -> bool:
        """
        Check if session time is expired
        :return:
        """
        result_bool = datetime.now() >= self.expires_at
        return result_bool

    def replace(self, new_session: BaseSession()) -> None:
        """
        :param BaseSession new_session: This is object where is fields the 'created_at' and 'exires_at' it's DateTime
        :return: None
        """
        self.session_id = new_session.session_id
        self.created_at = new_session.created_at
        assert new_session is not None
        if not isinstance(new_session, BaseSession):
            self.session_id = datetime.now().strftime("%F::%T.%f")
            self.created_at = datetime.now() + timedelta(hours=1)
        else:
            self.session_id = new_session.__getattribute__("session_id")
            self.created_at = new_session.__getattribute__("created_at")


class Database:

    def __init__(self, db_url: str) -> None:
        self.db_url: str = db_url
        self.is_async = self._check_async_url(db_url)
        self.engine = None
        self.session_factory = None

    def init_engine(self):
        """Инициализация движка в зависимости от типа"""
        if self.is_async:
            self.engine = create_async_engine(
                self.db_url, echo=True, pool_size=5, max_overflow=10
            )
            # self.session_factory = sessionmaker(
            #     bind=self.engine,
            #     class_=AsyncSession,
            #     autocommit=False,
            #     autoflush=False,
            # )
        else:
            self.engine = create_engine(
                self.db_url, echo=True, pool_size=5, max_overflow=10
            )
            # self.session_factory = sessionmaker(
            #     bind=self.engine,
            #     autocommit=False,
            #     autoflush=False,
            # )

    async def create_all_async(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def create_all(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def table_exists_create(self) -> bool:
        """Проверяет существование таблицы"""
        if not self.engine:
            self.init_engine()

        if self.is_async:
            # for async engine
            asyncio.run(self.create_all_async())
        else:
            # For sync engine
            self.create_all()

    def _check_async_url(self, db_url: str) -> bool:
        """Checking by URL What we have - sync or async engine"""

        return any(
            re.search(pattern, db_url)
            for pattern in [r"\+aiosqlite", r"\+asyncpg", r"\+asyncmy"]
        )

    async def drop_tables(self):
        if not self.engine:
            self.init_engine()

        if self.is_async:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        else:
            Base.metadata.drop_all(bind=self.engine)
