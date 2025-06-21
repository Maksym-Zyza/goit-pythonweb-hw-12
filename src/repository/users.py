from sqlalchemy.orm import Session
from typing import Optional

from src.database.models import User
from src.schemas.users import UserModel
from src.services.gravatar import generate_gravatar_url


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    Отримати користувача за email.

    Args:
        email (str): Email користувача.
        db (Session): Сесія бази даних.

    Returns:
        Optional[User]: Об'єкт користувача або None, якщо не знайдений.
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Створити нового користувача.

    Якщо у користувача немає аватара, генерує URL за допомогою Gravatar.

    Args:
        body (UserModel): Pydantic модель з даними користувача.
        db (Session): Сесія бази даних.

    Returns:
        User: Створений користувач.
    """
    new_user = User(**body.dict())
    if not new_user.avatar:
        new_user.avatar = generate_gravatar_url(new_user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token: str, db: Session) -> None:
    """
    Оновити refresh токен користувача.

    Args:
        user (User): Об'єкт користувача.
        refresh_token (str): Новий refresh токен.
        db (Session): Сесія бази даних.
    """
    user.refresh_token = refresh_token
    db.commit()


async def change_confirmed_email(email: str, db: Session) -> None:
    """
    Позначити email користувача як підтверджений.

    Args:
        email (str): Email користувача.
        db (Session): Сесія бази даних.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def get_users(db: Session) -> list[User]:
    """
    Отримати список усіх користувачів.

    Args:
        db (Session): Сесія бази даних.

    Returns:
        list[User]: Список користувачів.
    """
    users = db.query(User).all()
    return users


async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    Отримати користувача за ID.

    Args:
        user_id (int): Ідентифікатор користувача.
        db (Session): Сесія бази даних.

    Returns:
        Optional[User]: Користувач або None, якщо не знайдений.
    """
    user = db.query(User).filter_by(id=user_id).first()
    return user

async def get_user_by_email(email: str, db: Session):
    """
    Пошук користувача в базі даних за email.

    Args:
        email (str): Email користувача для пошуку.
        db (Session): Сесія SQLAlchemy для роботи з БД.

    Returns:
        User | None: Обʼєкт користувача, якщо знайдений, інакше None.
    """
    user = db.query(User).filter_by(email=email).first()
    return user


async def update_avatar_url(email: str, url: str, db: Session) -> User:
    """
    Оновити URL аватара користувача.

    Args:
        email (str): Email користувача.
        url (str): Новий URL аватара.
        db (Session): Сесія бази даних.

    Returns:
        User: Оновлений користувач.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
