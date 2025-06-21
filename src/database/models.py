import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Role(enum.Enum):
    """
    Enum ролей користувача.

    Attributes:
        admin (str): Роль адміністратора.
        user (str): Роль звичайного користувача.
    """

    admin: str = "admin"
    user: str = "user"


class User(Base):
    """
    Модель користувача.

    Attributes:
        id (int): Унікальний ідентифікатор користувача.
        username (str): Ім'я користувача.
        email (str): Електронна пошта користувача (унікальна).
        password (str): Хешований пароль.
        refresh_token (str, optional): Токен оновлення для авторизації.
        confirmed (bool): Чи підтверджено електронну пошту.
        avatar (str, optional): URL аватара.
        roles (Role): Роль користувача (admin або user).
        contacts (List[Contact]): Список контактів, пов’язаних з користувачем.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    roles = Column("roles", Enum(Role), default=Role.user)

    contacts = relationship("Contact", back_populates="owner", cascade="all, delete")


class Contact(Base):
    """
    Модель контакту.

    Attributes:
        id (int): Унікальний ідентифікатор контакту.
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (str): Електронна пошта контакту.
        phone (str): Номер телефону контакту.
        birthday (datetime, optional): Дата народження контакту.
        user_id (int): Ідентифікатор користувача, до якого належить контакт.
        owner (User): Зв’язок з користувачем-власником контакту.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    birthday = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="contacts")

    __table_args__ = (
        UniqueConstraint("user_id", "email", name="uix_user_email"),
        UniqueConstraint("user_id", "phone", name="uix_user_phone"),
    )
