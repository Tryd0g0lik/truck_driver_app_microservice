"""
__tests__/test_async_httpclient.py

For this test User need be - active, authorisation, having User-Agent - "AsyncHttpClient/1.0", and belong is in group admin or superuser
"""

import logging

import pytest
from project.asynchttp_client import AsyncHttpClient, HttpRequest, LocalApi
from project.middlewares import settings
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.mark.asyncio
async def test_async_http_client_valid():
    url = f"{settings.ALLOWED_ORIGINS[0]}{LocalApi.STR_TO_BINARY.value}"

    client = AsyncHttpClient()
    responses = await client.request(
        HttpRequest.POST.value, url=url, jsom_data={"data": ["Hallo word"]}
    )
    assert isinstance(responses, list)
    assert isinstance(responses[0], dict)
    assert "str_to_binary".startswith(list(responses[0].keys())[0])


@pytest.mark.asyncio
async def test_async_http_client_unvalidated():
    url = f"{settings.ALLOWED_ORIGINS[0]}/api/auth/binary/str_to_/"

    client = AsyncHttpClient()
    method = "POST"
    responses = await client.request(
        method, url=url, jsom_data={"data": ["Hallo word"]}
    )
    assert not isinstance(responses, list)
