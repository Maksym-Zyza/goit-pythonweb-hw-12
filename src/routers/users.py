"""
Маршрути для роботи з користувачами.

Доступні лише авторизованим користувачам. Переважно використовуються адміністраторами
для перегляду всіх користувачів, одного користувача по ID, а також для оновлення аватару.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Path, File
from sqlalchemy.orm import Session

from src.database.models import Role, User
from src.database.db import get_db
from src.schemas.users import UserResponse
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.upload_file import UploadFileService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth_service.get_current_user)],
)


@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """
    Отримати список усіх користувачів.

    Args:
        db (Session): Сесія бази даних.

    Returns:
        List[UserResponse]: Список користувачів.
    """
    users = await repository_users.get_users(db)
    return users


@router.get("/{user_id}", name="Get user by id", response_model=UserResponse)
async def get_users(user_id: int = Path(ge=1), db: Session = Depends(get_db)):
    """
    Отримати одного користувача за його ID.

    Args:
        user_id (int): Ідентифікатор користувача (>=1).
        db (Session): Сесія бази даних.

    Raises:
        HTTPException: Якщо користувача не знайдено.

    Returns:
        UserResponse: Дані користувача.
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Оновити аватар користувача. Доступно лише адміністраторам.

    Args:
        file (UploadFile): Новий аватар у форматі файлу.
        user (User): Поточний авторизований користувач.
        db (Session): Сесія бази даних.

    Raises:
        HTTPException: Якщо користувач не є адміністратором.
        HTTPException: Якщо користувача не знайдено.

    Returns:
        UserResponse: Оновлені дані користувача з новим аватаром.
    """
    if user.roles.value != Role.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can change the default avatar.",
        )

    avatar_url = UploadFileService().upload_file(file, user.username)
    user = await repository_users.update_avatar_url(user.email, avatar_url, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
