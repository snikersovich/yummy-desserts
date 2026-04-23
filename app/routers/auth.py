from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.data import get_user_by_email, create_user, verify_password, get_user_by_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_form(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "title": "Вход"
    })


@router.post("/login")
async def login_post(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный email или пароль",
            "title": "Вход"
        })

    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/register")
async def register_form(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error,
        "title": "Регистрация"
    })


@router.post("/register")
async def register_post(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    if get_user_by_email(db, email):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Пользователь с таким email уже существует",
            "title": "Регистрация"
        })

    from app.schemas import UserCreate
    user_data = UserCreate(email=email, password=password, full_name=full_name, phone=phone)
    user = create_user(db, user_data)

    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    return response


@router.get("/profile")
async def profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = get_user_by_id(db, int(user_id))
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "title": "Личный кабинет"
    })