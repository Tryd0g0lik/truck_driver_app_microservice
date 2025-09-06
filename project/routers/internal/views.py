from fastapi import Request, status, HTTPException, APIRouter
from starlette.responses import HTMLResponse, JSONResponse

from fastapi.templating import Jinja2Templates

render = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
def main_page(request: Request) -> JSONResponse:
    if not request:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error => 'request' not was found",
        )
    context = {"title": "First page"}
    return render.TemplateResponse(
        request, name="index.html", context=context, status=status.HTTP_200_OK
    )
