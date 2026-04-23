from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()


@router.post("/api/orders")
async def create_order(request: Request, db: Session = Depends(get_db)):
    print(f"👤 Пользователь из request.state.user: {request.state.user}")
    import uuid
    print("=" * 50)
    print("🔔 ПОЛУЧЕН ЗАПРОС НА СОЗДАНИЕ ЗАКАЗА")
    data = await request.json()
    print("📦 Данные заказа:", data)
    print("=" * 50)

    user_id = None
    user = request.state.user
    if user:
        user_id = user.id

    # Генерируем уникальный order_id, если его нет
    order_id = data.get("order_id")
    if not order_id:
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Извлекаем данные с проверкой на None
    customer = data.get("customer", {})
    delivery = data.get("delivery", {})

    order = models.Order(
        order_id=order_id,  # ← теперь точно не None
        user_id=user_id,
        guest_name=customer.get("name"),
        guest_phone=customer.get("phone"),
        guest_email=customer.get("email"),
        total_amount=data.get("total", 0),
        delivery_address=delivery.get("address"),
        delivery_date=delivery.get("date"),
        delivery_time=delivery.get("time"),
        payment_method=data.get("payment", "cash_on_delivery"),
        status="new"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Сохраняем товары
    for item in data.get("items", []):
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.get("product_id"),
            product_name=item.get("name"),
            product_price=item.get("base_price", item.get("price", 0)),
            quantity=item.get("quantity", 1)
        )
        db.add(order_item)
    db.commit()

    return {"status": "ok", "order_id": order.order_id}


@router.get("/api/my-orders")
async def get_my_orders(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        return []

    orders = db.query(models.Order).filter(
        models.Order.user_id == user.id
    ).order_by(
        models.Order.order_date.desc()
    ).all()

    result = []
    for order in orders:
        items = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == order.id
        ).all()
        result.append({
            "id": order.id,
            "order_id": order.order_id,
            "order_date": order.order_date.isoformat(),
            "total_amount": order.total_amount,
            "status": order.status,
            "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date,
            "delivery_time": order.delivery_time,
            "items": [{
                "product_name": item.product_name,
                "product_price": item.product_price,
                "quantity": item.quantity
            } for item in items]
        })

    return result


@router.get("/api/all-orders")
async def get_all_orders(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user or user.role != "admin":
        return []

    orders = db.query(models.Order).order_by(models.Order.order_date.desc()).all()

    result = []
    for order in orders:
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        result.append({
            "id": order.id,
            "order_id": order.order_id,
            "order_date": order.order_date.isoformat(),
            "total_amount": order.total_amount,
            "status": order.status,
            "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date,
            "delivery_time": order.delivery_time,
            "payment_method": order.payment_method,
            "customer_name": order.guest_name or (order.user.full_name if order.user else "Гость"),
            "customer_phone": order.guest_phone or (order.user.phone if order.user else "не указан"),
            "customer_email": order.guest_email or (order.user.email if order.user else "не указан"),
            "items": [{
                "product_name": item.product_name,
                "product_price": item.product_price,
                "quantity": item.quantity
            } for item in items]
        })

    return result