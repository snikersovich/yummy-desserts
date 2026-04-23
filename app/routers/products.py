from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.data import get_categories, get_category_by_slug

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/catalog")
async def catalog(
        request: Request,
        category: str = None,
        search: str = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    # Поиск по названию (регистронезависимый)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    products = query.all()

    # Получаем категории
    categories = get_categories(db)

    # Фильтр по категории (после поиска, чтобы не терять)
    if category:
        cat = get_category_by_slug(db, category)
        if cat:
            products = [p for p in products if p.category_id == cat.id]

    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "categories": categories,
        "products": products,
        "current_category": category,
        "search": search,
        "user": request.state.user,
        "title": "Каталог"
    })


@router.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "title": "Товар не найден"
        }, status_code=404)

    return templates.TemplateResponse("product.html", {
        "request": request,
        "product": product,
        "user": request.state.user,
        "title": product.name
    })