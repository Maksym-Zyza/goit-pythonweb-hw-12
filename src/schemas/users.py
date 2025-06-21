"""
Схеми Pydantic для моделі користувача.

Використовуються для реєстрації, автентифікації, відповіді API та запитів на email/скидання паролю.
"""

from pydantic import BaseModel, EmailStr, Field
from src.database.models import Role


class UserModel(BaseModel):
    """
    Схема для реєстрації нового користувача.

    Attributes:
        username (str): Унікальне ім'я користувача.
        email (EmailStr): Email користувача.
        password (str): Пароль користувача.
    """

    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Схема відповіді при запиті даних користувача.

    Attributes:
        id (int): Унікальний ідентифікатор користувача.
        username (str): Ім'я користувача.
        email (str): Email користувача.
        avatar (str): URL до аватару користувача.
        roles (Role): Роль користувача (admin, user тощо).
    """

    id: int
    username: str
    email: str
    avatar: str
    roles: Role

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    """
    Схема токена доступу (JWT), який повертається при логіні.

    Attributes:
        access_token (str): JWT токен доступу.
        token_type (str): Тип токена (звичайно "bearer").
    """

    access_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Схема для запиту, який містить лише email.

    Використовується для надсилання листа з підтвердженням або скиданням паролю.

    Attributes:
        email (EmailStr): Email користувача.
    """

    email: EmailStr


class ResetPasswordModel(BaseModel):
    """
    Схема для скидання паролю користувача.

    Attributes:
        password (str): Новий пароль (мінімум 6 символів).
    """

    password: str = Field(min_length=6)
