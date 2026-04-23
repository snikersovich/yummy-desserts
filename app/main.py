from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app import models
from app.routers import pages, auth, products, cart, admin_products, admin_orders, api_orders
from app.data import create_categories, create_sample_products

# Создаем таблицы в БД
models.Base.metadata.create_all(bind=engine)

# Заполняем начальными данными
def init_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        create_categories(db)
        create_sample_products(db)
        # Создаем админа, если нет
        from app.auth import hash_password
        admin = db.query(models.User).filter(models.User.email == "admin@yummy.ru").first()
        if not admin:
            admin = models.User(
                email="admin@yummy.ru",
                password_hash=hash_password("admin123"),
                full_name="Администратор",
                phone="+7 (999) 123-45-67",
                role="admin"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

init_db()

app = FastAPI(title="Yummy Desserts")

# Подключаем статику
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")

# Middleware для передачи пользователя
@app.middleware("http")
async def add_user_to_context(request: Request, call_next):
    from app.dependencies import get_current_user
    user = get_current_user(request)
    request.state.user = user
    response = await call_next(request)
    return response

# Подключаем роутеры
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(admin_products.router)
app.include_router(admin_orders.router)
app.include_router(api_orders.router)