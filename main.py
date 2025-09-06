import asyncio
import os
from http.client import HTTPException

from fastapi import FastAPI, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from rich import status
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from project.routers.internal.views import router as interal_router

from dotenv_ import (
    BASE_DIR,
    APP_HOST,
    APP_PORT,
)
from project.db.corn import Settings
from project.middlewares import CustomHeaderMiddleware

settings = Settings()
# JINJA

middleware_list = [
    Middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        expose_headers=["X-CSRF-Token", "http"],
        # allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    ),
    Middleware(CustomHeaderMiddleware, secret_key=settings.SECRET_KEY),
]

static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created directory: {static_dir}")

app = FastAPI(
    title="Truck Driver",
    version="0.1.0",
    description="App where truck-driver is working with a map.",
    middleware=middleware_list,
)
app.include_router(interal_router)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=int(APP_PORT),
        reload=True,
        reload_dirs=["project"],  # direction for reload
    )
