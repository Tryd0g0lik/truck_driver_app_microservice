import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union
import json
from enum import Enum
from fastapi import status
from fastapi.responses import Response
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


class ContentType(Enum):
    DEFAULT = "application/json"
    FORMDATA = "multipart/form-data"


class AsyncHttpClient:
    """
    This client is built on the library aiohttp
    """

    message = "AsyncHttpClient"

    def __init__(self, timeout: int = 30, verify_ssl: bool = True) -> None:
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.headers = {
            "User-Agent": "AsyncHttpClient/1.0",
            "Accept": ContentType.DEFAULT,
            "Content-Type": ContentType.DEFAULT,
        }

    async def request(
        self,
        method: str,
        url: HttpRequest,
        access=ContentType.DEFAULT,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, Any], str] = None,
        jsom_data: Optional[Any] = None,
        headers: Optional[Dict["str", str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
    ) -> Response:
        """
        Async HTTP request.
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
                    test = await response.text()
                    context = test.strip()
                    try:
                        # try to get the json
                        if (
                            response.headers.get("content-type", "")
                            .lower()
                            .startswith(access)
                            .lower()
                        ):
                            context = await response.json()
                    except json.JSONDecodeError as error:
                        message += "".join(
                            [
                                ".",
                                self.request.__name__,
                                "ERROR => ",
                                error.args[0].strip(),
                            ]
                        )
                        log.error(message)
                        return Response(
                            {"data": message},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

                    return Response(
                        {"data": context},
                        headers=response.headers.copy(),
                        status_code=status.HTTP_200_OK,
                    )
            except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as error:
                message += "".join(
                    [".", self.request.__name__, "ERROR => ", error.args[0].strip()]
                )
                log.error(message)
                return Response(
                    {"data": message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
