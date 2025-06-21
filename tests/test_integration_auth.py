from unittest.mock import Mock
from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {"username": "test", "email": "test@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Account already exists"


def test_login_unconfirmed(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not confirmed"


def test_login_confirmed_email(client):
    session = TestingSessionLocal()
    try:
        user = session.query(User).filter(User.email == user_data["email"]).first()
        user.confirmed = True
        session.commit()
    finally:
        session.close()

    response = client.post(
        "/api/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_wrong_password_login(client):
    session = TestingSessionLocal()
    try:
        user = session.query(User).filter(User.email == user_data["email"]).first()
        user.confirmed = True
        session.commit()
    finally:
        session.close()

    response = client.post(
        "/api/auth/login",
        data={
            "username": user_data["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


def test_wrong_email_login(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wrong@email.com",
            "password": user_data["password"],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email"


def test_validation_error_login(client):
    response = client.post("/api/auth/login", data={"password": user_data["password"]})
    assert response.status_code == 422
    assert "detail" in response.json()
