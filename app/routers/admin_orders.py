from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def check_admin(request: Request):
    user = request.state.user
    if not user or user.role != "admin":
        return False
    return True


@router.get("/admin/orders")
async def admin_orders(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    orders = db.query(models.Order).order_by(models.Order.order_date.desc()).all()

    return templates.TemplateResponse("admin/orders.html", {
        "request": request,
        "orders": orders,
        "user": request.state.user,
        "title": "Управление заказами"
    })


@router.post("/admin/order/update/{order_id}")
async def update_order_status(
        request: Request,
        order_id: int,
        status: str,
        db: Session = Depends(get_db)
):
    if not check_admin(request):
        return {"error": "Unauthorized"}

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        return {"status": "ok"}
    return {"error": "Order not found"}