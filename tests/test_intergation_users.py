import pytest
from main import app
from src.database.models import User, Role
from src.services.auth import auth_service
from src.schemas.users import UserResponse

test_admin_user = User(
    id=1,
    username="admin",
    email="admin@example.com",
    roles=Role.admin,
    confirmed=True,
    password="123456789",
    avatar="http://example.com/avatar.png",
)

test_normal_user = User(
    id=2,
    username="user",
    email="user@example.com",
    roles=Role.user,
    confirmed=True,
    password="123456789",
    avatar="http://example.com/avatar.png",
)


@pytest.fixture
def override_auth_admin():
    async def fake_get_current_user():
        return test_admin_user

    app.dependency_overrides[auth_service.get_current_user] = fake_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_auth_user():
    async def fake_get_current_user():
        return test_normal_user

    app.dependency_overrides[auth_service.get_current_user] = fake_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.mark.usefixtures("override_auth_admin")
def test_get_users(client, monkeypatch):
    async def mock_get_users(db):
        return [
            UserResponse.from_orm(test_admin_user),
            UserResponse.from_orm(test_normal_user),
        ]

    monkeypatch.setattr("src.repository.users.get_users", mock_get_users)

    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["username"] == "admin"
    assert data[1]["email"] == "user@example.com"


@pytest.mark.usefixtures("override_auth_admin")
def test_get_user_by_id_found(client, monkeypatch):
    async def mock_get_user_by_id(user_id, db):
        if user_id == test_admin_user.id:
            return UserResponse.from_orm(test_admin_user)
        return None

    monkeypatch.setattr("src.repository.users.get_user_by_id", mock_get_user_by_id)

    response = client.get(f"/api/users/{test_admin_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"


@pytest.mark.usefixtures("override_auth_admin")
def test_get_user_by_id_not_found(client, monkeypatch):
    async def mock_get_user_by_id(user_id, db):
        return None

    monkeypatch.setattr("src.repository.users.get_user_by_id", mock_get_user_by_id)

    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


@pytest.mark.usefixtures("override_auth_admin")
def test_update_avatar_user_admin(client, monkeypatch):
    async def mock_update_avatar_url(email, avatar_url, db):
        return UserResponse.from_orm(test_admin_user)

    monkeypatch.setattr(
        "src.repository.users.update_avatar_url", mock_update_avatar_url
    )

    monkeypatch.setattr(
        "src.services.upload_file.UploadFileService.upload_file",
        lambda self, file, username: "http://example.com/avatar.png",
    )

    response = client.patch(
        "/api/users/avatar", files={"file": ("avatar.png", b"filecontent")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_admin_user.username
