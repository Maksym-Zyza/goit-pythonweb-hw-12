"""
Контролери для роботи з контактами користувача.

Маршрути реалізують функціонал:
- створення контакту
- отримання списку контактів з фільтрами
- перегляд одного контакту
- редагування
- видалення
- пошук днів народження протягом 7 днів

Доступ тільки для авторизованих користувачів.
"""

from fastapi import APIRouter, Depends, Query, status
from src.database.db import get_db
from src.repository import contacts as repository
from src.services.auth import auth_service
from src.schemas import contacts as schemas
from typing import Optional
from src.database.models import User

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
    dependencies=[Depends(auth_service.get_current_user)],
)


@router.get("/", name="List of contacts")
async def get_contacts(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db=Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Отримати список контактів користувача з опціональним фільтром по імені, прізвищу та email.

    Args:
        first_name (Optional[str]): Фільтр за іменем.
        last_name (Optional[str]): Фільтр за прізвищем.
        email (Optional[str]): Фільтр за email.
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        List[ContactResponse]: Список контактів користувача.
    """
    contacts = await repository.search_contacts(
        first_name, last_name, email, db, current_user
    )
    return contacts


@router.post(
    "/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED
)
async def create_contact(
    body: schemas.ContactModelRegister,
    db=Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Створити новий контакт для користувача.

    Args:
        body (ContactModelRegister): Дані нового контакту.
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Створений контакт.
    """
    contact = await repository.create_contact(body, db, current_user)
    return contact


@router.get("/birthdays", name="Upcoming birthdays (7 days)")
async def get_upcoming_birthdays(
    db=Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Отримати список контактів, у яких день народження протягом наступних 7 днів.

    Args:
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        List[ContactResponse]: Список контактів з майбутніми днями народження.
    """
    contacts = await repository.get_upcoming_birthdays(db, current_user)
    return contacts


@router.get("/{id}", name="Get contact by id")
async def get_contact_by_id(
    id: int,
    db=Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Отримати контакт за його унікальним ідентифікатором.

    Args:
        id (int): Ідентифікатор контакту.
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Знайдений контакт.
    """
    contact = await repository.get_contact_by_id(id, db, current_user)
    return contact


@router.put("/{id}", response_model=schemas.ContactResponse)
async def update_contact(
    id: int,
    body: schemas.ContactModelRegister,
    db=Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Оновити існуючий контакт користувача.

    Args:
        id (int): Ідентифікатор контакту.
        body (ContactModelRegister): Оновлені дані контакту.
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Оновлений контакт.
    """
    contact = await repository.update_contact(id, body, db, current_user)
    return contact


@router.delete("/{id}", response_model=schemas.ContactResponse)
async def delete_contact(
    id: int,
    db=Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Видалити контакт за його ідентифікатором.

    Args:
        id (int): Ідентифікатор контакту.
        db (Session): Сесія бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Видалений контакт.
    """
    contact = await repository.delete_contact(id, db, current_user)
    return contact
