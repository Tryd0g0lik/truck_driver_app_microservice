from fastapi  import Request
from starlette.responses import HTMLResponse
from main import render, app

app.get(path="/")
def main_page(request: Request) -> HTMLResponse:
    context = {}
    return render(request, name="index.html", context=context, status=200)