import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from src.database.models import Contact, User
from src.repository import contacts as contact_repo
from src.schemas.contacts import ContactModelRegister


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.fixture
def contact():
    return Contact(
        id=1,
        first_name="John",
        last_name="Jonson",
        email="john@example.com",
        phone="1234567890",
        birthday=datetime(1990, 6, 25).date(),
        user_id=1,
    )


@pytest.mark.asyncio
async def test_search_contacts(mock_session, user, contact):
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [contact]
    mock_session.query.return_value.filter.return_value = mock_query

    result = await contact_repo.search_contacts("John", None, None, mock_session, user)

    assert result == [contact]


@pytest.mark.asyncio
async def test_create_contact_success(mock_session, user):
    body = ContactModelRegister(
        first_name="Pitter",
        last_name="Smith",
        email="jane@example.com",
        phone="1234567890",
        birthday=datetime(1992, 7, 1).date(),
    )
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await contact_repo.create_contact(body, mock_session, user)

    assert isinstance(result, Contact)
    assert result.first_name == body.first_name
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_contact_integrity_error(mock_session, user):
    body = ContactModelRegister(
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="1234567890",
        birthday=datetime(1992, 7, 1).date(),
    )
    mock_session.commit.side_effect = IntegrityError(None, None, None)

    with pytest.raises(Exception) as excinfo:
        await contact_repo.create_contact(body, mock_session, user)

    assert excinfo.value.status_code == 400


@pytest.mark.asyncio
async def test_get_contact_by_id_found(mock_session, user, contact):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = contact
    mock_session.query.return_value = mock_query

    result = await contact_repo.get_contact_by_id(1, mock_session, user)

    assert result == contact


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(mock_session, user):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with pytest.raises(Exception) as excinfo:
        await contact_repo.get_contact_by_id(1, mock_session, user)

    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_update_contact_success(mock_session, user, contact):
    body = ContactModelRegister(
        first_name="Updated",
        last_name="User",
        email="updated@example.com",
        phone="0987654321",
        birthday=datetime(1993, 8, 15).date(),
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = contact
    mock_session.query.return_value = mock_query

    result = await contact_repo.update_contact(1, body, mock_session, user)

    assert result.first_name == "Updated"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_contact_not_found(mock_session, user):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    body = ContactModelRegister(
        first_name="NotFound",
        last_name="User",
        email="no@example.com",
        phone="0000000000",
        birthday=datetime(2000, 1, 1).date(),
    )

    with pytest.raises(Exception) as excinfo:
        await contact_repo.update_contact(1, body, mock_session, user)

    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_success(mock_session, user, contact):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = contact
    mock_session.query.return_value = mock_query

    result = await contact_repo.delete_contact(1, mock_session, user)

    assert result == contact
    mock_session.delete.assert_called_once_with(contact)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_contact_not_found(mock_session, user):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with pytest.raises(Exception) as excinfo:
        await contact_repo.delete_contact(1, mock_session, user)

    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(mock_session, user, contact):
    today = datetime.today().date()
    contact.birthday = today + timedelta(days=3)

    mock_query = MagicMock()
    mock_filter_1 = MagicMock()
    mock_filter_2 = MagicMock()
    mock_filter_2.all.return_value = [contact]

    mock_filter_1.filter.return_value = mock_filter_2
    mock_query.filter.return_value = mock_filter_1
    mock_session.query.return_value = mock_query

    result = await contact_repo.get_upcoming_birthdays(mock_session, user)

    assert contact in result
