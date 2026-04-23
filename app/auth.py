import hashlib
from typing import Optional


# Простое хэширование паролей
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# Моковые пользователи (потом заменим на БД)
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


def get_user_by_email(email: str) -> Optional[dict]:
    for user in USERS:
        if user["email"] == email:
            return user
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    for user in USERS:
        if user["id"] == user_id:
            return user
    return None


def create_user(email: str, password: str, full_name: str, phone: str) -> dict:
    new_id = max([u["id"] for u in USERS]) + 1 if USERS else 1
    new_user = {
        "id": new_id,
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "phone": phone,
        "role": "customer",
        "created_at": "2025-01-01"
    }
    USERS.append(new_user)
    return new_user