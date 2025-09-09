import logging
import pytest
import re
from uuid_extensions import uuid7

from __tests__.fixtures import drop_test, async_engine
from project.db.models import SessionUserModel, Database

from main import settings
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)
# Names columns list

session_id: str = "061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6"


class TestSessionUserModel:

    @pytest.mark.asyncio
    async def test_session_user_model_structure(self, async_engine) -> None:
        """
        THis test check exists the db, simply.
        :param async_engine:
        :return:
        """
        expected_columns_list = [
            "session",
            "created_at",
            "expires_at",
        ]
        async with async_engine().engine.begin() as conn:
            # Checking exists the table 'session'
            assert SessionUserModel.__tablename__ == "session"
            # CHECK columns
            columns = [col.name for col in SessionUserModel.__table__.columns]
            assert all(coll in columns for coll in expected_columns_list)
            await conn.close()

    @pytest.mark.asyncio
    async def test_session_user_required_fields(self, drop_test) -> None:
        """
        This test is:
         1) creates a one view of line/row;
         2) then, below created rows select and check;
         3) after the  all cheks - delete the all rows;
         Here i use different the connections for a check - how will be work it on an async engine.
        :return: None
        """
        from sqlalchemy import text, insert, delete

        db = Database(settings.DATABASE_URL_SQLITE)
        db.init_engine()
        async with db.engine.begin() as conn:
            """ "1) Async engine/ CREATING the single row"""
            session_id_ = str(uuid7())
            await conn.execute(
                insert(SessionUserModel).values(session_id=f"{session_id_}")
            )
            await conn.commit()
        async with db.engine.connect() as conn:
            """ "2) Async engine/ CHECKING above created the single row"""
            result = await conn.execute(text("""SELECT * FROM session"""))
            respon = result.fetchall()
            # CHECK
            assert type(respon) == list
            assert len(respon) >= 1
            regex = r"([a-zA-A0-9][a-zA-A0-9-]*[a-zA-A0-9]$)"
            result_bool = True if re.fullmatch(regex, list(respon[-1])[1]) else False
            assert True == result_bool
            assert list(respon[-1])[1] == str(session_id_)
        """3) Async engine. DELETE the all views/rows in relational db"""
        await drop_test()
