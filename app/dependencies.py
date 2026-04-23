from fastapi import Request
from app.data import get_user_by_id
from app.database import SessionLocal


def get_current_user(request: Request):
    user_id = request.cookies.get("user_id")
    print(f"🍪 Cookie user_id: {user_id}")  # ← эта строка для отладки

    if user_id:
        db = SessionLocal()
        try:
            user = get_user_by_id(db, int(user_id))
            print(f"👤 Найден пользователь: {user.email if user else None}")  # ← эта строка
            return user
        finally:
            db.close()
    return None