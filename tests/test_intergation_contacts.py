import pytest
from src.schemas.contacts import ContactResponse, ContactModelRegister
from src.database.models import User
from src.services.auth import auth_service
from main import app


test_user = User(
    id=1,
    username="testuser",
    email="test@example.com",
    roles="user",
    confirmed=True,
    password="hashedpassword",
    avatar="http://example.com/avatar.png",
)

test_contact_data = {
    "first_name": "Rob",
    "last_name": "Anderson",
    "email": "rob@example.com",
    "phone": "0671234567",
    "birthday": "1990-01-01",
}


@pytest.fixture
def override_auth_user():
    async def fake_get_current_user():
        return test_user

    app.dependency_overrides[auth_service.get_current_user] = fake_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_get_contacts(client, monkeypatch):
    async def mock_search_contacts(first_name, last_name, email, db, current_user):
        return [ContactResponse(id=1, **test_contact_data)]

    monkeypatch.setattr("src.repository.contacts.search_contacts", mock_search_contacts)

    response = client.get("/api/contacts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "Rob"


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_create_contact(client, monkeypatch):
    contact_in = ContactModelRegister(**test_contact_data)
    contact_out = ContactResponse(id=1, **test_contact_data)

    async def mock_create_contact(body, db, current_user):
        return contact_out

    monkeypatch.setattr("src.repository.contacts.create_contact", mock_create_contact)

    response = client.post("/api/contacts/", json=test_contact_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == contact_in.email


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_get_contact_by_id(client, monkeypatch):
    contact_out = ContactResponse(id=1, **test_contact_data)

    async def mock_get_contact_by_id(id, db, current_user):
        return contact_out

    monkeypatch.setattr(
        "src.repository.contacts.get_contact_by_id", mock_get_contact_by_id
    )

    response = client.get("/api/contacts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["first_name"] == "Rob"


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_update_contact(client, monkeypatch):
    updated_data = {**test_contact_data, "first_name": "Jane"}
    contact_out = ContactResponse(id=1, **updated_data)

    async def mock_update_contact(id, body, db, current_user):
        return contact_out

    monkeypatch.setattr("src.repository.contacts.update_contact", mock_update_contact)

    response = client.put("/api/contacts/1", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_delete_contact(client, monkeypatch):
    contact_out = ContactResponse(id=1, **test_contact_data)

    async def mock_delete_contact(id, db, current_user):
        return contact_out

    monkeypatch.setattr("src.repository.contacts.delete_contact", mock_delete_contact)

    response = client.delete("/api/contacts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


@pytest.mark.usefixtures("override_auth_user")
@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, monkeypatch):
    contacts = [ContactResponse(id=1, **test_contact_data)]

    async def mock_get_upcoming_birthdays(db, current_user):
        return contacts

    monkeypatch.setattr(
        "src.repository.contacts.get_upcoming_birthdays", mock_get_upcoming_birthdays
    )

    response = client.get("/api/contacts/birthdays")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "Rob"
