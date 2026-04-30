from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/items", response_class=HTMLResponse)
async def items_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("items.html", {"request": request})


@router.get("/tictactoe", response_class=HTMLResponse)
async def tictactoe_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("tictactoe.html", {"request": request})


@router.get("/tictactoe-online", response_class=HTMLResponse)
async def tictactoe_online_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("tictactoe_online.html", {"request": request})
@router.get("/reversi", response_class=HTMLResponse)
async def reversi_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("reversi.html", {"request": request})
