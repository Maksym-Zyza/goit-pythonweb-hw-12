import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User, Contact
from src.database.db import get_db
from src.schemas.contacts import ContactModelRegister
from src.services.auth import Auth
from main import app

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

test_user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "123456789",
    "roles": "user",
}


@pytest.fixture(scope="session", autouse=True)
def init_models():
    """Ініціалізація тестової БД: дроп + створення схем + користувач"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    hashed_pw = Auth().get_password_hash(test_user_data["password"])
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=hashed_pw,
        confirmed=True,
        avatar="https://example.com/avatar.jpg",
        roles=test_user_data["roles"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    test_user_data["id"] = user.id
    db.close()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    token = Auth().create_access_token({"sub": test_user_data["email"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake_upload_file():
    mock_file = MagicMock()
    mock_file.file = MagicMock()
    mock_file.filename = "avatar.png"
    return mock_file


@pytest.fixture
def user():
    return User(id=1, username="testuser", roles="user")


@pytest.fixture
def contact(user: User):
    return Contact(
        id=1,
        name="Robert",
        surname="Anderson",
        email="Robert@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
        user=user,
    )


@pytest.fixture
def contact_body():
    return ContactModelRegister(
        name="Robert",
        surname="Anderson",
        email="evan@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
    )
