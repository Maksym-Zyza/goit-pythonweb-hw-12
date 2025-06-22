import os
from dotenv import load_dotenv
import redis
import pickle
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # Bearer token
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from src.repository.users import get_user_by_email
from src.database.db import get_db
from src.services.redis_config import get_redis_client


load_dotenv()

ALGORITHM = os.getenv("HASH_ALGORITHM")
SECRET_KEY = os.getenv("HASH_SECRET")


class Auth:
    """
    Сервіс автентифікації для роботи з паролями, JWT токенами та кешуванням користувачів.

    Атрибути:
        pwd_context (CryptContext): Контекст для хешування паролів.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 схема для отримання токенів.
        r (redis.Redis): Підключення до Redis для кешування користувачів.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = get_redis_client()

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє відповідність відкритого пароля та хешу.

        Args:
            plain_password (str): Відкритий пароль.
            hashed_password (str): Хешований пароль.

        Returns:
            bool: True, якщо пароль співпадає з хешем, інакше False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Хешує пароль.

        Args:
            password (str): Відкритий пароль.

        Returns:
            str: Хешований пароль.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: float = 15):
        """
        Генерує JWT токен доступу.

        Args:
            data (dict): Дані для кодування в токен (наприклад, {"sub": email}).
            expires_delta (float, optional): Тривалість дії токена у хвилинах (за замовчуванням 15).

        Returns:
            str: Закодований JWT токен.
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_access_token

    def create_email_token(self, data: dict):
        """
        Генерує JWT токен для підтвердження email з терміном дії 1 година.

        Args:
            data (dict): Дані для кодування в токен.

        Returns:
            str: Закодований JWT токен підтвердження email.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        Отримує поточного користувача з токена.

        Декодує JWT, перевіряє scope, намагається взяти користувача з Redis кешу,
        якщо немає — звертається до бази даних і кешує результат.

        Args:
            token (str): JWT токен доступу.
            db (Session): Сесія бази даних.

        Raises:
            HTTPException: Якщо токен недійсний або користувача не знайдено.

        Returns:
            User: Об’єкт користувача.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        # user = await repository_users.get_user_by_email(email, db)
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise credentials_exception
        return user

    def get_email_from_token(self, token: str):
        """
        Витягує email з JWT токена підтвердження email.

        Args:
            token (str): JWT токен.

        Raises:
            HTTPException: Якщо токен недійсний або має неправильний scope.

        Returns:
            str: Email із токена.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
