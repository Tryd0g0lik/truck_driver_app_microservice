import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union
from enum import Enum
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class HttpRequest(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class LocalApi(Enum):
    STR_TO_BINARY = "/api/auth/binary/str_to_binary/"


class ContentType(Enum):
    DEFAULT = "application/json"
    FORMDATA = "multipart/form-data"


class AsyncHttpClient:
    """
    This client is built on the library aiohttp.
    "User-Agent": "AsyncHttpClient/1.0",
    Example:
    ```
        client = AsyncHttpClient()
        method = "POST"
        responses = await client.request(
            method, url=url, jsom_data={"string": ["Hallo word"]}
        )
    ```
    """

    message = "AsyncHttpClient"

    def __init__(self, timeout: int = 30, verify_ssl: bool = True) -> None:
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.headers = {
            "User-Agent": "AsyncHttpClient/1.0",
            "Accept": ContentType.DEFAULT.value,
            "Content-Type": ContentType.DEFAULT.value,
        }

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        jsom_data: Optional[Union[Dict[str, Any], Any]] = None,
        headers: Optional[Dict["str", str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
    ) -> dict:
        """
        Async HTTP request for
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        async with aiohttp.ClientSession(
            timeout=self.timeout, headers=self.headers
        ) as session:
            message = ""
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=jsom_data,
                    auth=auth,
                ) as response:
                    context = await response.json()
                    log.info(context)

                    return context

            except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as error:
                message += "".join(
                    [".", self.request.__name__, "ERROR => ", str(error)]
                )
                log.error(message)
                return {"data": message}
