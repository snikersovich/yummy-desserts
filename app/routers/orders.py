from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import json

router = APIRouter()


@router.post("/api/orders")
async def create_order(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    user_id = None
    user = request.state.user
    if user:
        user_id = user.id

    order = models.Order(
        order_id=data.get("order_id"),
        user_id=user_id,
        guest_name=data.get("customer", {}).get("name"),
        guest_phone=data.get("customer", {}).get("phone"),
        guest_email=data.get("customer", {}).get("email"),
        total_amount=data.get("total"),
        delivery_address=data.get("delivery", {}).get("address"),
        delivery_date=data.get("delivery", {}).get("date"),
        delivery_time=data.get("delivery", {}).get("time"),
        payment_method=data.get("payment"),
        status="new"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Сохраняем товары в заказе
    for item in data.get("items", []):
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.get("product_id"),
            product_name=item.get("name"),
            product_price=item.get("base_price"),
            quantity=item.get("quantity")
        )
        db.add(order_item)
    db.commit()

    return {"status": "ok", "order_id": order.order_id}