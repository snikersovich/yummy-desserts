from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/cart")
async def cart(request: Request):
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "user": request.state.user,
        "title": "Корзина"
    })


@router.get("/checkout")
async def checkout(request: Request):
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "user": request.state.user,
        "title": "Оформление заказа"
    })