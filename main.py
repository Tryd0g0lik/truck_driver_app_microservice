import os
from fastapi import  FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
BASE_DIR = os.path.realpath(os.path.dirname(__file__))
render = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created directory: {static_dir}")

app = FastAPI(
    title="Truck Driver",
    version="0.1.0",
    description="App where truck-driver is working with a map."
)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


