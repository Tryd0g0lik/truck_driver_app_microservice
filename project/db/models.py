"""
project/db/models.py
"""

import asyncio
import logging
import re
from sqlalchemy.orm import validates, Session

from pydantic import BaseModel, ConfigDict

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ColumnElement,
    create_engine,
)
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

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
        String(40),
        unique=True,
        nullable=False,
        comment="Session ID for anyone of user/ Min length 30 and max length 40 symbols",
    )
    created_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime, default=lambda: datetime.now() + timedelta(hours=1))

    @validates("session_id")
    def validate_session_id_regex(self, key, session_id: str) -> str:
        regex = r"([a-zA-A0-9][a-zA-A0-9-]*[a-zA-A0-9]$)"
        if not re.fullmatch(regex, session_id):
            raise ValueError(
                "%s: Session_id don't match regex"
                % (self.validate_session_id_regex.__name__,)
            )
        log.info(
            "%s: Session ID regex matched: %s"
            % (self.validate_session_id_regex.__name__, session_id)
        )

        # Valid the length of session_id
        if len(session_id) < 30:
            raise ValueError(
                "%s: Session ID must be at least 30 characters long"
                % (self.validate_session_id_regex.__name__,)
            )
        if len(session_id) > 40:
            raise ValueError(
                "%s: Session ID must be at exceed 40 characters"
                % (self.validate_session_id_regex.__name__,)
            )
        return session_id

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
    def __init__(self, path_in_db: str) -> None:
        """
        :param db_url: str This is url/path to the database
        :param is_async: bool
        engine = None
        session_factory = None or sessionmaker(engine)
        :param db_url:
        Example:
        ````
        db = Database(settings.DATABASE_URL_SQLITE)

        async def test_records():
            db = Database(settings.DATABASE_URL_SQLITE)
            db.init_engine()

            async with db.engine.connect() as conn:
                result = await conn.execute(text'''SELECT * FROM session'''))
                respon = result.fetchall()
                assert type(respon) == list
                assert  len(respon) >= 1
                regex = r'([a-zA-A0-9][a-zA-A0-9-]*[a-zA-A0-9]$)'
                result_bool = True if re.fullmatch(regex, list(respon[0])[1]) else False
                assert True == result_bool
            ```
        """
        self.path_in_db: str = path_in_db
        self.is_async = self._check_async_url(path_in_db)
        self.engine = None
        self.session_factory: Session = None

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
                self.path_in_db, echo=True, pool_size=5, max_overflow=10
            )
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                # class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            )
        else:
            self.engine = create_engine(
                self.path_in_db, echo=True, pool_size=5, max_overflow=10
            )
            # self.session_factory = sessionmaker(
            #     bind=self.engine,
            #     autocommit=False,
            #     autoflush=False,
            # )

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
