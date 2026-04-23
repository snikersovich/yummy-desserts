from fastapi import APIRouter, Request, Form, HTTPException, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from app import models
from app.database import get_db
from app.data import (
    get_products, get_product_by_id, create_product,
    update_product, delete_product, get_categories
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Папка для загрузки фото
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(uploaded_file: UploadFile) -> str:
    """Сохраняет загруженный файл и возвращает путь к нему"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return f"/uploads/{safe_filename}"


def check_admin(request: Request):
    """Проверка, что пользователь админ"""
    user = request.state.user
    if not user or user.role != "admin":
        return False
    return True


# ========== АДМИН-ПАНЕЛЬ ==========

@router.get("/admin")
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    products = get_products(db)
    categories = get_categories(db)

    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "products": products,
        "categories": categories,
        "user": request.state.user,
        "title": "Админ-панель"
    })


@router.get("/admin/product/add")
async def admin_add_product_form(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    categories = get_categories(db)

    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "categories": categories,
        "product": None,
        "user": request.state.user,
        "title": "Добавить товар"
    })


@router.post("/admin/product/add")
async def admin_add_product(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1),
        image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    image_url = "https://via.placeholder.com/300x200?text=🍰+Новый"
    if image and image.filename:
        try:
            image_url = save_uploaded_file(image)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")

    from app.schemas import ProductCreate
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        in_stock=in_stock,
        category_id=category_id,
        preparation_days=preparation_days
    )

    create_product(db, product_data)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/product/edit/{product_id}")
async def admin_edit_product_form(
        request: Request,
        product_id: int,
        db: Session = Depends(get_db)
):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    categories = get_categories(db)

    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "categories": categories,
        "product": product,
        "user": request.state.user,
        "title": "Редактировать товар"
    })


@router.post("/admin/product/edit/{product_id}")
async def admin_edit_product(
        request: Request,
        product_id: int,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        in_stock: bool = Form(False),
        preparation_days: int = Form(1),
        image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Обработка нового изображения
    image_url = product.image_url
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

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "category_id": category_id,
        "in_stock": in_stock,
        "preparation_days": preparation_days,
        "image_url": image_url,
    }

    update_product(db, product_id, product_data)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/product/delete/{product_id}")
async def admin_delete_product(
        request: Request,
        product_id: int,
        db: Session = Depends(get_db)
):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    product = get_product_by_id(db, product_id)
    if product:
        image_url = product.image_url
        if image_url and not image_url.startswith("https://"):
            old_path = os.path.join(UPLOAD_DIR, os.path.basename(image_url))
            if os.path.exists(old_path):
                os.remove(old_path)

    delete_product(db, product_id)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/clear-users")
async def clear_users(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse(url="/login", status_code=303)

    from app.auth import hash_password

    # Удаляем всех пользователей кроме админа
    db.query(models.User).filter(models.User.role != "admin").delete()

    # Обновляем админа
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

    return RedirectResponse(url="/admin", status_code=303)