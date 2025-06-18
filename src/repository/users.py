from sqlalchemy.orm import Session
from typing import Optional

from src.database.models import User
from src.schemas.users import UserModel
from src.services.gravatar import generate_gravatar_url


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    new_user = User(**body.dict())
    if not new_user.avatar:
        new_user.avatar = generate_gravatar_url(new_user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    user.refresh_token = refresh_token
    db.commit()


async def change_confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def get_users(db: Session):
    users = db.query(User).all()
    return users


async def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter_by(id=user_id).first()
    return user


async def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter_by(email=email).first()
    return user


async def update_avatar_url(email: str, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
