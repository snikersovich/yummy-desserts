from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.data import get_categories, get_products

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    categories = get_categories(db)
    products = get_products(db, limit=4)  # первые 4 товара для популярных
    return templates.TemplateResponse("index.html", {
        "request": request,
        "categories": categories,
        "popular_products": products,
        "user": request.state.user,
        "title": "Yummy Desserts"
    })


@router.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "user": request.state.user,
        "title": "О нас"
    })


@router.get("/contacts")
async def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {
        "request": request,
        "user": request.state.user,
        "title": "Контакты"
    })


@router.get("/howto")
async def howto(request: Request):
    return templates.TemplateResponse("howto.html", {
        "request": request,
        "user": request.state.user,
        "title": "Как заказать"
    })