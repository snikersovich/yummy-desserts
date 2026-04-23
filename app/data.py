from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import hash_password, verify_password

# ========== USERS ==========
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        phone=user.phone,
        role="customer"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ========== CATEGORIES ==========
def get_categories(db: Session):
    return db.query(models.Category).all()

def get_category_by_slug(db: Session, slug: str):
    return db.query(models.Category).filter(models.Category.slug == slug).first()

def create_categories(db: Session):
    """Заполнение категорий при первом запуске"""
    categories = [
        {"id": 1, "name": "Трайфлы", "slug": "trayfly", "icon": "🍰"},
        {"id": 2, "name": "Капкейки", "slug": "kapkeyki", "icon": "🧁"},
        {"id": 3, "name": "Рулеты", "slug": "rulety", "icon": "🍥"},
    ]
    for cat in categories:
        if not db.query(models.Category).filter(models.Category.id == cat["id"]).first():
            db.add(models.Category(**cat))
    db.commit()

# ========== PRODUCTS ==========
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products_by_category(db: Session, category_id: int):
    return db.query(models.Product).filter(models.Product.category_id == category_id).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_data: dict):
    db_product = get_product_by_id(db, product_id)
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product


def create_sample_products(db: Session):
    """Заполнение товарами при первом запуске"""
    products = [
        {"id": 1, "name": "Трайфл Сникерс", "description": "Шоколадный бисквит, карамель, арахис", "price": 1300, "image_url": "/static/images/products/snikers.jpg", "in_stock": True, "category_id": 1, "preparation_days": 1},
        {"id": 2, "name": "Трайфл Баннофи Пай", "description": "Сладкий банан, сливочная карамель", "price": 1300, "image_url": "/static/images/products/bannofi.jpg", "in_stock": True, "category_id": 1, "preparation_days": 1},
        {"id": 3, "name": "Трайфл Красный бархат", "description": "Бисквит красный бархат, ягодная начинка", "price": 1300, "image_url": "/static/images/products/red_velvet.jpg", "in_stock": True, "category_id": 1, "preparation_days": 1},
        {"id": 4, "name": "Трайфл Твикс", "description": "Хрустящий слой с печеньем, карамель", "price": 1300, "image_url": "/static/images/products/twix.jpg", "in_stock": True, "category_id": 1, "preparation_days": 1},
        {"id": 5, "name": "Трайфл Орео", "description": "Шоколадный бисквит, крем орео", "price": 1300, "image_url": "/static/images/products/oreo.jpg", "in_stock": True, "category_id": 1, "preparation_days": 1},
        {"id": 6, "name": "Капкейк с вишней", "description": "Ванильная основа, вишнёвая начинка", "price": 1000, "image_url": "/static/images/products/cupcake_cherry.jpg", "in_stock": True, "category_id": 2, "preparation_days": 1},
        {"id": 7, "name": "Капкейк с малиной", "description": "Ванильная основа, малиновая начинка", "price": 1000, "image_url": "/static/images/products/cupcake_raspberry.jpg", "in_stock": True, "category_id": 2, "preparation_days": 1},
        {"id": 8, "name": "Капкейк с карамелью", "description": "Ванильная основа, карамельная начинка", "price": 1000, "image_url": "/static/images/products/cupcake_caramel.jpg", "in_stock": True, "category_id": 2, "preparation_days": 1},
        {"id": 9, "name": "Мереговый рулет классический", "description": "Нежный меренговый рулет", "price": 1500, "image_url": "/static/images/products/meringue_classic.jpg", "in_stock": True, "category_id": 3, "preparation_days": 1},
        {"id": 10, "name": "Мереговый рулет с ягодами", "description": "Нежный меренговый рулет с ягодами", "price": 2000, "image_url": "/static/images/products/meringue_berries.jpg", "in_stock": True, "category_id": 3, "preparation_days": 1},
    ]
    for prod in products:
        if not db.query(models.Product).filter(models.Product.id == prod["id"]).first():
            db.add(models.Product(**prod))
    db.commit()