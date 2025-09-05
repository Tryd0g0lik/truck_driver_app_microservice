import asyncio
import os
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


from dotenv_ import (
    BASE_DIR,
    APP_HOST,
    APP_PORT,
)
from project.db.corn import Settings
from project.middleware import CustomHeaderMiddleware

settings = Settings()
# JINJA
render = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
middleware_list = [
    Middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=[
            "accept",
            "accept-encoding",
            "Authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
            "Accept-Language",
            "Content-Language",
        ],
        expose_headers=["X-CSRF-Token", "http"],
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
