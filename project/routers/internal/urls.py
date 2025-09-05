from fastapi import Request, status, HTTPException
from starlette.responses import HTMLResponse
from main import render, app

app.get(path="/")


def main_page(request: Request) -> HTMLResponse:
    if not request:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error => 'request' not was found",
        )
    context = {}
    return render(
        request, name="index.html", context=context, status=status.HTTP_200_OK
    )
