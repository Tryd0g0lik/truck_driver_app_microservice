import logging

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from logs import configure_logging

from project.middlewares import settings

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class Test_SessionUserModel:

    @pytest.mark.parametrize(
        "session_id, expected",
        [
            ("061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6-d44a7ee025", False),
            ("061cb8fe-0f0b-7c39-8003 d44a7ee0bdf6", False),
            ("061cb8fe0f0b7c398003d44a7ee0bdf6", False),
            ("061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6%", False),
            ("%061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6", False),
            ("061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6 ", False),
            (" 061cb8fe-0f0b-7c39-8003-d44a7ee0bdf6", False),
            (" ", False),
            ("061cb8fe-0f0b", False),
        ],
    )
    @pytest.mark.asyncio
    async def test_session_user_required_fields_unvalided(
        self, session_id: str, expected: bool
    ) -> None:
        """This testing the validation from models. Initially is all parameters is unvalidated.
        Finite response should be the False.
        """
        from sqlalchemy.ext.asyncio import async_sessionmaker
        from project.db.models import SessionUserModel

        engine: AsyncEngine = create_async_engine(settings.DATABASE_URL_SQLITE)
        Session = async_sessionmaker(bind=engine)

        async with Session() as conn:
            try:
                not_valid_session = SessionUserModel(session_id=str(session_id))
                conn.add(not_valid_session)
                await conn.commit()
            except Exception as eerror:
                log.info(eerror.args[0])
                assert False == expected
