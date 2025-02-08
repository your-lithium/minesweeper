from fastapi import APIRouter, Request

from app.core import jinja2_templates


main_router = APIRouter(
    tags=["main"],
)


@main_router.get("/")
async def index(request: Request):
    return jinja2_templates.TemplateResponse("index.html", context={"request": request})

@main_router.get("/create")
async def create(request: Request, mode: str):
    if mode == "Small: 9×9, 10 mines":
        rows, columns, mines = 9, 9, 10
    elif mode == "Medium: 16×16, 40 mines":
        rows, columns, mines  = 16, 16, 40
    elif mode == "Hard: 30×16, 99 mines":
        rows, columns, mines  = 30, 16, 99
    elif mode == "Extreme: 24×30, 160 mines":
        rows, columns, mines  = 24, 30, 160
    return jinja2_templates.TemplateResponse(
        "game.html", context={"request": request, "rows": rows, "columns": columns, "mines": mines}
    )
