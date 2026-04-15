from pydantic import BaseModel
import hashlib
from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional
import os
import shutil
from datetime import datetime

def hash_password(password: str) -> str:
    """Простое хэширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return hash_password(plain_password) == hashed_password


app = FastAPI(title="Yummy Desserts")

# Подключаем статику (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")

# ========== МОКОВЫЕ ДАННЫЕ ==========

# Категории товаров (обновлено под реальный ассортимент)
CATEGORIES = [
    {"id": 1, "name": "Трайфлы", "slug": "trayfly", "icon": "🍰"},
    {"id": 2, "name": "Капкейки", "slug": "kapkeyki", "icon": "🧁"},
    {"id": 3, "name": "Рулеты", "slug": "rulety", "icon": "🍥"},
]

# Товары из реального прайс-листа с фото
POPULAR_PRODUCTS = [
    # Трайфлы
    {
        "id": 1,
        "name": "Трайфл Сникерс",
        "description": "Шоколадный бисквит, карамель, арахис, нежный крем",
        "price": 1300,
        "image_url": "/static/images/products/snikers.jpg",
        "in_stock": True,
        "category_id": 1,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1300, "6": 1600, "9": 2100}
    },
    {
        "id": 2,
        "name": "Трайфл Баннофи Пай",
        "description": "Сладкий банан, сливочная карамель, хрустящее печенье",
        "price": 1300,
        "image_url": "/static/images/products/bannofi.jpg",
        "in_stock": True,
        "category_id": 1,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1300, "6": 1600, "9": 2100}
    },
    {
        "id": 3,
        "name": "Трайфл Красный бархат",
        "description": "Бисквит красный бархат, ягодная начинка",
        "price": 1300,
        "image_url": "/static/images/products/red_velvet.jpg",
        "in_stock": True,
        "category_id": 1,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1300, "6": 1600, "9": 2100}
    },
    {
        "id": 4,
        "name": "Трайфл Твикс",
        "description": "Хрустящий слой с печеньем, сливочная карамель, шоколадный бисквит",
        "price": 1300,
        "image_url": "/static/images/products/twix.jpg",
        "in_stock": True,
        "category_id": 1,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1300, "6": 1600, "9": 2100}
    },
    {
        "id": 5,
        "name": "Трайфл Орео",
        "description": "Шоколадный бисквит, сливочный крем орео",
        "price": 1300,
        "image_url": "/static/images/products/oreo.jpg",
        "in_stock": True,
        "category_id": 1,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1300, "6": 1600, "9": 2100}
    },
    # Капкейки
    {
        "id": 6,
        "name": "Капкейк с вишней",
        "description": "Ванильная/шоколадная основа, вишнёвая начинка, крем чиз",
        "price": 1000,
        "image_url": "/static/images/products/cupcake_cherry.jpg",
        "in_stock": True,
        "category_id": 2,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1000, "6": 1500, "9": 2000}
    },
    {
        "id": 7,
        "name": "Капкейк с малиной",
        "description": "Ванильная/шоколадная основа, малиновая начинка, крем чиз",
        "price": 1000,
        "image_url": "/static/images/products/cupcake_raspberry.jpg",
        "in_stock": True,
        "category_id": 2,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1000, "6": 1500, "9": 2000}
    },
    {
        "id": 8,
        "name": "Капкейк с карамелью",
        "description": "Ванильная/шоколадная основа, карамельная начинка, крем чиз",
        "price": 1000,
        "image_url": "/static/images/products/cupcake_caramel.jpg",
        "in_stock": True,
        "category_id": 2,
        "preparation_days": 1,
        "has_sizes": True,
        "sizes": [4, 6, 9],
        "price_by_size": {"4": 1000, "6": 1500, "9": 2000}
    },
    # Мереговый рулет
    {
        "id": 9,
        "name": "Мереговый рулет классический",
        "description": "Нежный меренговый рулет без украшений",
        "price": 1500,
        "image_url": "/static/images/products/meringue_classic.jpg",
        "in_stock": True,
        "category_id": 3,
        "preparation_days": 1,
        "has_sizes": False,
    },
    {
        "id": 10,
        "name": "Мереговый рулет со свежими ягодами",
        "description": "Нежный меренговый рулет со свежими ягодами",
        "price": 2000,
        "image_url": "/static/images/products/meringue_berries.jpg",
        "in_stock": True,
        "category_id": 3,
        "preparation_days": 1,
        "has_sizes": False,
    },
]

# Моковые данные для пользователей (временно, потом в БД)
USERS = [
    {
        "id": 1,
        "email": "admin@yummy.ru",
        "password_hash": hash_password("admin123"),
        "full_name": "Администратор",
        "phone": "+7 (999) 123-45-67",
        "role": "admin",
        "created_at": "2025-01-01"
    }
]

def get_user_by_email(email: str):
    """Находит пользователя по email"""
    for user in USERS:
        if user["email"] == email:
            return user
    return None


def create_user(email: str, password: str, full_name: str, phone: str):
    """Создаёт нового пользователя"""
    new_id = max([u["id"] for u in USERS]) + 1 if USERS else 1
    new_user = {
        "id": new_id,
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "phone": phone,
        "role": "customer",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    USERS.append(new_user)
    return new_user

# ========== КЛИЕНТСКАЯ ЧАСТЬ ==========


@app.get("/")
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": CATEGORIES,
            "popular_products": POPULAR_PRODUCTS,
            "title": "Yummy Desserts",
        },
    )


@app.get("/catalog")
async def catalog(request: Request, category: str = None):
    """Страница каталога с фильтром по категориям"""
    products = POPULAR_PRODUCTS.copy()

    if category:
        cat = next((c for c in CATEGORIES if c["slug"] == category), None)
        if cat:
            products = [p for p in products if p["category_id"] == cat["id"]]

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "categories": CATEGORIES,
            "products": products,
            "current_category": category,
            "title": "Каталог",
        },
    )


@app.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int):
    """Страница товара с выбором размера"""
    product = next((p for p in POPULAR_PRODUCTS if p["id"] == product_id), None)

    if not product:
        product = POPULAR_PRODUCTS[0]

    return templates.TemplateResponse(
        "product.html",
        {
            "request": request,
            "product": product,
            "title": product["name"],
        },
    )


@app.get("/cart")
async def cart(request: Request):
    """Страница корзины"""
    return templates.TemplateResponse("cart.html", {"request": request, "title": "Корзина"})


@app.get("/checkout")
async def checkout(request: Request):
    """Страница оформления заказа"""
    return templates.TemplateResponse("checkout.html", {"request": request, "title": "Оформление заказа"})


@app.get("/contacts")
async def contacts(request: Request):
    """Страница контактов"""
    return templates.TemplateResponse("contacts.html", {"request": request, "title": "Контакты"})


@app.get("/howto")
async def howto(request: Request):
    """Страница 'Как заказать'"""
    return templates.TemplateResponse("howto.html", {"request": request, "title": "Как заказать"})


@app.get("/about")
async def about(request: Request):
    """Страница 'О нас' с отзывами и примерами работ"""
    # Моковые отзывы
    reviews = [
        {"name": "Анна", "text": "Заказывала торт на день рождения! Очень вкусно, красиво оформлен. Спасибо!",
         "rating": 5},
        {"name": "Екатерина", "text": "Капкейки просто бомба! Нежные, воздушные, начинка отличная.", "rating": 5},
        {"name": "Мария", "text": "Мереговый рулет - нежность! Обязательно закажу ещё.", "rating": 5},
        {"name": "Ольга", "text": "Быстрая доставка, вежливый курьер. Десерты свежие и очень вкусные.", "rating": 5},
    ]
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "reviews": reviews,
            "title": "О нас"
        }
    )


@app.get("/login")
async def login_form(request: Request, error: str = None):
    """Страница входа"""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": error,
            "title": "Вход"
        }
    )


@app.get("/register")
async def register_form(request: Request, error: str = None):
    """Страница регистрации"""
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "error": error,
            "title": "Регистрация"
        }
    )


@app.post("/register")
async def register_post(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        password: str = Form(...)
):
    """Обработка регистрации"""
    # Проверяем, не существует ли пользователь
    if get_user_by_email(email):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует",
                "title": "Регистрация"
            }
        )

    # Создаём пользователя
    user = create_user(email, password, full_name, phone)

    # Создаём сессию (просто сохраняем в cookie)
    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="user_id", value=str(user["id"]), httponly=True)
    response.set_cookie(key="user_email", value=user["email"], httponly=True)

    return response


@app.post("/login")
async def login_post(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):
    """Обработка входа"""
    user = get_user_by_email(email)

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный email или пароль",
                "title": "Вход"
            }
        )

    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="user_id", value=str(user["id"]), httponly=True)
    response.set_cookie(key="user_email", value=user["email"], httponly=True)
    response.set_cookie(key="user_name", value=user["full_name"], httponly=True)

    return response


@app.get("/logout")
async def logout():
    """Выход из аккаунта"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    response.delete_cookie("user_email")
    response.delete_cookie("user_name")
    return response


@app.get("/profile")
async def profile(request: Request):
    """Личный кабинет пользователя"""
    # Получаем ID пользователя из cookie
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Находим пользователя
    user = next((u for u in USERS if str(u["id"]) == user_id), None)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # Получаем заказы пользователя из localStorage (передаём на клиент)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "title": "Личный кабинет"
        }
    )

# ========== АДМИН-ПАНЕЛЬ ==========


@app.get("/admin")
async def admin_panel(request: Request):
    """Админ-панель - список товаров"""
    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "products": POPULAR_PRODUCTS,
            "categories": CATEGORIES,
            "title": "Админ-панель"
        }
    )


@app.get("/admin/product/add")
async def admin_add_product_form(request: Request):
    """Форма добавления товара"""
    return templates.TemplateResponse(
        "admin/product_form.html",
        {
            "request": request,
            "categories": CATEGORIES,
            "product": None,
            "title": "Добавить товар"
        }
    )


@app.post("/admin/product/add")
async def admin_add_product(
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1)
):
    """Добавление товара"""
    new_id = max([p["id"] for p in POPULAR_PRODUCTS]) + 1 if POPULAR_PRODUCTS else 1

    new_product = {
        "id": new_id,
        "name": name,
        "description": description,
        "price": price,
        "image_url": "https://via.placeholder.com/300x200?text=🍰+Новый",
        "in_stock": in_stock,
        "category_id": category_id,
        "preparation_days": preparation_days,
        "has_sizes": False,
    }

    POPULAR_PRODUCTS.append(new_product)
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/product/edit/{product_id}")
async def admin_edit_product_form(request: Request, product_id: int):
    """Форма редактирования товара"""
    product = next((p for p in POPULAR_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return templates.TemplateResponse(
        "admin/product_form.html",
        {
            "request": request,
            "categories": CATEGORIES,
            "product": product,
            "title": "Редактировать товар"
        }
    )


@app.post("/admin/product/edit/{product_id}")
async def admin_edit_product(
        product_id: int,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1)
):
    """Сохранение редактирования товара"""
    for i, p in enumerate(POPULAR_PRODUCTS):
        if p["id"] == product_id:
            POPULAR_PRODUCTS[i] = {
                **p,
                "name": name,
                "description": description,
                "price": price,
                "category_id": category_id,
                "in_stock": in_stock,
                "preparation_days": preparation_days,
            }
            break

    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/product/delete/{product_id}")
async def admin_delete_product(product_id: int):
    """Удаление товара"""
    global POPULAR_PRODUCTS
    POPULAR_PRODUCTS = [p for p in POPULAR_PRODUCTS if p["id"] != product_id]
    return RedirectResponse(url="/admin", status_code=303)


# ========== УПРАВЛЕНИЕ ЗАКАЗАМИ (АДМИНКА) ==========

@app.get("/admin/orders")
async def admin_orders(request: Request):
    """Страница управления заказами в админке"""
    # Получаем все заказы из localStorage (через клиент)
    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "title": "Управление заказами"
        }
    )


@app.post("/admin/order/update/{order_id}")
async def admin_update_order_status(order_id: str, status: str = Form(...)):
    """Обновление статуса заказа"""
    # Этот эндпоинт будет обновлять статус через JS
    return {"status": "ok", "order_id": order_id, "new_status": status}


# ========== РАБОТА С ИЗОБРАЖЕНИЯМИ ==========

# Создаём папку для загрузок, если её нет
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Подключаем папку uploads к статике
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def save_uploaded_file(uploaded_file: UploadFile) -> str:
    """Сохраняет загруженный файл и возвращает путь к нему"""
    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    # Возвращаем URL для доступа
    return f"/uploads/{safe_filename}"


@app.post("/admin/product/add")
async def admin_add_product(
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1),
        image: UploadFile = File(None)
):
    """Добавление товара с загрузкой изображения"""
    new_id = max([p["id"] for p in POPULAR_PRODUCTS]) + 1 if POPULAR_PRODUCTS else 1

    # Обработка изображения
    image_url = "https://via.placeholder.com/300x200?text=🍰+Новый"
    if image and image.filename:
        try:
            image_url = save_uploaded_file(image)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")

    new_product = {
        "id": new_id,
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url,
        "in_stock": in_stock,
        "category_id": category_id,
        "preparation_days": preparation_days,
        "has_sizes": False,
    }

    POPULAR_PRODUCTS.append(new_product)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/product/edit/{product_id}")
async def admin_edit_product(
        product_id: int,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1),
        image: UploadFile = File(None)
):
    """Сохранение редактирования товара с возможностью загрузить новое фото"""
    for i, p in enumerate(POPULAR_PRODUCTS):
        if p["id"] == product_id:
            # Обработка нового изображения
            image_url = p.get("image_url")
            if image and image.filename:
                try:
                    # Удаляем старое фото, если оно не заглушка
                    if image_url and not image_url.startswith("https://"):
                        old_path = os.path.join(UPLOAD_DIR, os.path.basename(image_url))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    image_url = save_uploaded_file(image)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")

            POPULAR_PRODUCTS[i] = {
                **p,
                "name": name,
                "description": description,
                "price": price,
                "category_id": category_id,
                "in_stock": in_stock,
                "preparation_days": preparation_days,
                "image_url": image_url,
            }
            break

    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/product/delete/{product_id}")
async def admin_delete_product(product_id: int):
    """Удаление товара вместе с его изображением"""
    global POPULAR_PRODUCTS

    # Находим товар и удаляем его фото
    product = next((p for p in POPULAR_PRODUCTS if p["id"] == product_id), None)
    if product:
        image_url = product.get("image_url")
        if image_url and not image_url.startswith("https://"):
            old_path = os.path.join(UPLOAD_DIR, os.path.basename(image_url))
            if os.path.exists(old_path):
                os.remove(old_path)

    POPULAR_PRODUCTS = [p for p in POPULAR_PRODUCTS if p["id"] != product_id]
    return RedirectResponse(url="/admin", status_code=303)
