from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from src.database.models import Base
from src.database.db import engine
from src.database.db import get_db
from src.routers import contacts, auth, users

app = FastAPI()
"""
Головний FastAPI додаток.

Ініціалізує CORS middleware, підключає маршрутизатори, створює таблиці в базі даних на старті,
та обробляє винятки, наприклад перевищення ліміту запитів.
"""

limiter = Limiter(key_func=get_remote_address)
"""
Обʼєкт для лімітування швидкості запитів на основі IP-адреси клієнта.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
Додає CORS middleware для дозволу запитів з frontend-адрес.
"""


@app.on_event("startup")
async def create_tables():
    """
    Подія запуску сервера.

    Створює всі таблиці у базі даних згідно моделей SQLAlchemy.
    """
    Base.metadata.create_all(engine)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробник помилки перевищення ліміту запитів.

    Args:
        request (Request): HTTP запит.
        exc (RateLimitExceeded): Виняток перевищення ліміту.

    Returns:
        JSONResponse: Відповідь з кодом 429 і повідомленням про ліміт.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


@app.get("/", name="API root")
def get_index():
    """
    Корінне API.

    Returns:
        dict: Привітальне повідомлення.
    """
    return {"message": "Welcome to root API"}


@app.get("/health", name="Server availability")
def get_health(db=Depends(get_db)):
    """
    Перевірка стану сервера та бази даних.

    Args:
        db (Session): Сесія бази даних.

    Raises:
        HTTPException: Якщо база даних не працює.

    Returns:
        dict: Повідомлення про готовність API.
    """
    try:
        result = db.execute(text("SELECT 1+1")).fetchone()
        if result is None:
            raise Exception("DB check failed")

        return {"message": "API is up and ready for the requests"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DB is not configured correctly",
        )


@app.get("/me", name="Route with rate limiting")
@limiter.limit("5/minute")
async def my_endpoint(request: Request):
    """
    Маршрут з лімітом в 5 запитів на хвилину.

    Args:
        request (Request): HTTP запит.

    Returns:
        dict: Повідомлення про доступ до маршруту.
    """
    return {"message": "This is my route with rate limiting."}


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
