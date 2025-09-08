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

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, sessionmaker
from watchfiles import awatch

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

    def replace(self, new_session: BaseSession) -> None:
        """
        :param BaseSession new_session: This is object where is fields the 'created_at' and 'exires_at' it's DateTime
        :return: None
        """
        if new_session is not None:
            raise ValueError("new_session cannot be None")

        if not isinstance(new_session, BaseSession):
            log.info(
                "%s: new_session not be of type BaseSession"
                % (SessionUserModel.__class__.__name__ + "." + self.replace.__name__,)
            )
            self.session_id = datetime.now().strftime("%F::%T.%f")
            self.created_at = datetime.now() + timedelta(hours=1)
        else:
            log.info(
                "%s: new_session is type BaseSession"
                % (SessionUserModel.__class__.__name__ + "." + self.replace.__name__,)
            )
            self.session_id = new_session.__getattribute__("session_id")
            self.created_at = new_session.__getattribute__("created_at")


class Database:
    def __init__(self, db_url: str) -> None:
        """
        :param db_url: str This is url/path to the database
        :param is_async: bool
        engine = None
        session_factory = None
        :param db_url:
        Example:
        ````python
        db = Database(settings.DATABASE_URL_SQLITE)

        async def test_records():
            db() # Here we define the engine.
            session = Session(db.engine)
            async with db.session_factory() as session:
                session_user_ = SessionUserModel( session_id="dsasda")
                session.add(session_user_)
                await session.commit()
        ```
        """
        self.db_url: str = db_url
        self.is_async = self._check_async_url(db_url)
        self.engine = None
        self.session_factory = None

    def init_engine(self) -> None:
        """
        Here we define the engine. It could be how async or sync.
        Type of engine be depend from url to the db file.
        '.table_exists_create()' - create the tables from models.
        Example: ```python
            db = Database(settings.DATABASE_URL_SQLITE)
            db.init_engine() # Here we definning and gets the engine.
            # further
            db.engine # <sqlalchemy.ext.asyncio.engine.AsyncEngine object at 0x0000028691D50690>
        ````
        :return:
        """
        if self.is_async:
            self.engine = create_async_engine(
                self.db_url, echo=True, pool_size=5, max_overflow=10
            )
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            )
        else:
            self.engine = create_engine(
                self.db_url, echo=True, pool_size=5, max_overflow=10
            )
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            )

    async def __create_all_async(self) -> None:
        """
        Here we getting the ASYNC connection on database and creating all tables.
        :return: None
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def __create_all(self) -> None:
        """
        Here we create all tables. Engine need only SYNC.
        :return: None
        """
        Base.metadata.create_all(bind=self.engine)

    async def table_exists_create(self) -> None:
        """
        Check exists the engine and if the engine is not exists wil be run '.init_engine()'.
        Further, creates the tables (from models).
        :return:None
        """
        if not self.engine:
            self.init_engine()

        if self.is_async:
            # for async engine
            return await asyncio.create_task(self.__create_all_async())
        else:
            # For sync engine
            return self.__create_all()

    def _check_async_url(self, db_url: str) -> bool:
        """Checking by URL What we have - sync or async engine"""

        return any(
            re.search(pattern, db_url)
            for pattern in [r"\+aiosqlite", r"\+asyncpg", r"\+asyncmy"]
        )

    async def is_table_exists_async(self, engine, table_nane: str = "session") -> bool:
        """
        ASYNC method. His task is to check the existence of table.
        RUn only if engine is async.
        :param engine: async of engine.
        :param table_nane: str. Default is value 'session'.

        Example:\
        '''
        # Get engine\
        db.init_engine()\
        # Check the table 'session'.\
        result = await db.is_table_exists_async(db.engine)\
        # If false, means what we will be creating the tables from models.\
        if not result:\
            await db.table_exists_create()\
        '''
        :return: True or Fasle
        """

        from sqlalchemy import text

        async with engine.connect() as conn:
            try:
                result = await conn.execute(
                    text("""SELECT %s FROM %s WHERE id  >  0""" % (1, table_nane)),
                )
                pass
                if result and result.fetchone():
                    return True
            except Exception as error:
                logging.error(
                    "%s ERROR => %s"
                    % (self.is_table_exists_async.__name__, error.args[0])
                )
                return False
        return False

    async def drop_tables(self) -> None:
        if not self.engine:
            self.init_engine()

        if self.is_async:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        else:
            Base.metadata.drop_all(bind=self.engine)
