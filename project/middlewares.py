"""
project/middlewares.py
"""

import secrets
from enum import Enum

from fastapi import Request, Response, HTTPException, status, FastAPI
from typing import Callable, Awaitable, Union
from starlette.middleware.base import BaseHTTPMiddleware


from dotenv_ import DEBUG

from project.db.corn import Settings

settings = Settings()


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str, cookie_name: str = "csrf_token") -> None:
        """
        https://www.starlette.io/middleware/#BaseHTTPMiddleware
        :param app:
        :param secret_key:
        :param cookie_name:
        """
        super().__init__(app)
        self.secret_key: str = secret_key
        self.cookie_name: str = cookie_name
        self.csrf_token: str | None = None

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # For don't danger the http methods - Here, install the CSRF-token in cookie
        if request.method in settings.ALLOWED_METHODS[:4]:
            # Check - Do we have a CSRF-token in cookie
            if not request.cookies.get(self.cookie_name):
                response = await call_next(request)
                # Create the CSRF-token & install in cookie
                csrf_token = "".join(
                    [
                        self.secret_key.replace("-", ""),
                        "Bearer",
                        secrets.token_urlsafe(32),
                    ]
                )
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=False,
                    samesite=settings.CSRF_COOKIE_SAMESITE,
                    secure=not DEBUG,
                    max_age=settings.CSRF_COOKIE_MAX_AGE,
                )
                return response
            else:
                # If we installed earlier - the CSRF-token
                return await call_next(request)

        # For danger the http methods -  Here, install the CSRF-token in cookie
        elif request.method in settings.ALLOWED_METHODS[4:]:

            # Checkin equality between an app'n secret_key and X-CSRF-Token from request's header
            csrf_header = request.headers.get("X-CSRF-Token").split("Bearer")[0]
            if (
                not csrf_header
                or not self.secret_key
                or csrf_header != self.secret_key.replace("-", "")
            ):

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF Token"
                )
            return await call_next(request)

        # For some html methods.
        else:
            return await call_next(request)


class JWTTokenName(Enum):
    ACCESS = "token_access"
    REFRESH = "token_refresh"


# JWT-token
class CustomJWTMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: FastAPI, header_name: JWTTokenName = JWTTokenName.ACCESS.value
    ) -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        jwt_token = ""
        if list(request.headers.keys()):
            # ACCESS token
            if JWTTokenName.ACCESS.value in list(request.headers.keys()):
                jwt_token += "".join([request.headers[JWTTokenName.ACCESS.value]])
            # REFRESH token
            elif JWTTokenName.REFRESH.name in list(request.headers.keys()):
                jwt_token += "".join([request.headers[JWTTokenName.REFRESH.name]])
            if len(jwt_token) == 0:
                return await call_next(request)
            #

        return await call_next(request)
