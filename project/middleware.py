import secrets
from fastapi import Request, Response, HTTPException, status

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
        self.secret_key = secret_key
        self.cookie_name = cookie_name

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        # for not a danger the methods of requests
        if request.method in settings.ALLOWED_METHODS[:4]:

            # Install the CSRF-token in cookie
            if not request.cookies.get(self.cookie_name):
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=False,
                    samesite=settings.CSRF_COOKIE_SAMESITE is str,
                    secure=not DEBUG,
                )
            response.status_code = status.HTTP_200_OK
            return response

        # for a danger the methods of requests
        csrf_cookie = request.cookies.get(self.cookie_name)
        if request.method in settings.ALLOWED_METHODS[4:]:
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF Token"
                )
            response.status_code = status.HTTP_201_CREATED
            return response
        return response
