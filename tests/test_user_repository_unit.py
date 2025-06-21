import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel
from src.repository import users as user_repo


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password="1234567",
        confirmed=False,
        avatar=None,
        refresh_token=None,
    )


@pytest.mark.asyncio
async def test_get_user_by_email(mock_session, user):
    filter_by_mock = MagicMock()
    filter_by_mock.first.return_value = user
    mock_session.query.return_value.filter_by.return_value = filter_by_mock

    result = await user_repo.get_user_by_email("test@example.com", mock_session)

    assert result == user
    mock_session.query.return_value.filter_by.assert_called_once_with(
        email="test@example.com"
    )


@pytest.mark.asyncio
@patch("src.repository.users.generate_gravatar_url")
async def test_create_user(mock_generate_gravatar, mock_session):
    user_data = UserModel(
        username="newuser", email="new@example.com", password="securepassword"
    )
    mock_generate_gravatar.return_value = "http://gravatar.com/avatar"

    result = await user_repo.create_user(user_data, mock_session)

    assert isinstance(result, User)
    assert result.email == "new@example.com"
    assert result.avatar == "http://gravatar.com/avatar"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_update_token(mock_session, user):
    await user_repo.update_token(user, "new_refresh_token", mock_session)

    assert user.refresh_token == "new_refresh_token"
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_change_confirmed_email(mock_session, user):
    with patch("src.repository.users.get_user_by_email", return_value=user):
        await user_repo.change_confirmed_email("test@example.com", mock_session)

    assert user.confirmed is True
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_users(mock_session, user):
    mock_session.query().all.return_value = [user]

    result = await user_repo.get_users(mock_session)

    assert len(result) == 1
    assert result[0] == user


@pytest.mark.asyncio
async def test_get_user_by_id(mock_session, user):
    filter_by_mock = MagicMock()
    filter_by_mock.first.return_value = user
    mock_session.query.return_value.filter_by.return_value = filter_by_mock

    result = await user_repo.get_user_by_id(1, mock_session)

    assert result == user
    mock_session.query.return_value.filter_by.assert_called_once_with(id=1)


@pytest.mark.asyncio
async def test_update_avatar_url(mock_session, user):
    with patch("src.repository.users.get_user_by_email", return_value=user):
        result = await user_repo.update_avatar_url(
            "test@example.com", "http://new-avatar.com", mock_session
        )

    assert result.avatar == "http://new-avatar.com"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user)
