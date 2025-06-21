"""
Схеми Pydantic для моделі контактів.

Використовуються для валідації вхідних/вихідних даних при створенні,
оновленні та перегляді контактів.
"""

from pydantic import BaseModel, EmailStr
from datetime import date


class ContactModelRegister(BaseModel):
    """
    Схема для створення або оновлення контакту.

    Attributes:
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Email адреса контакту.
        phone (str): Номер телефону контакту.
        birthday (date): Дата народження контакту.
    """

    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(ContactModelRegister):
    """
    Схема відповіді при запиті контакту (включає ID).

    Наслідує всі поля з ContactModelRegister і додає унікальний ідентифікатор.

    Attributes:
        id (int): Унікальний ідентифікатор контакту.
    """

    id: int
