import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_supabase, get_supabase_admin, get_current_user


def make_mock_user(user_id="test-user-id", email="test@example.com"):
    user = MagicMock()
    user.id = user_id
    user.email = email
    user.created_at = "2026-01-01T00:00:00Z"
    return user


def make_mock_supabase():
    mock = MagicMock()
    mock.auth.sign_up = MagicMock()
    mock.auth.sign_in_with_password = MagicMock()
    mock.auth.refresh_session = MagicMock()
    mock.auth.sign_out = MagicMock()
    mock.auth.reset_password_email = MagicMock()
    mock.auth.get_user = MagicMock()
    mock.auth.admin.delete_user = MagicMock()
    mock.auth.admin.sign_out = MagicMock()
    # Table query chain mock
    table_mock = MagicMock()
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.delete.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.range.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[])
    mock.table.return_value = table_mock
    return mock


@pytest.fixture
def mock_supabase():
    return make_mock_supabase()


@pytest.fixture
def mock_user():
    return make_mock_user()


@pytest.fixture
def client(mock_supabase, mock_user):
    app.dependency_overrides[get_supabase] = lambda: mock_supabase
    app.dependency_overrides[get_supabase_admin] = lambda: mock_supabase
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth(mock_supabase):
    """Client without auth override — for testing unauthenticated routes."""
    app.dependency_overrides[get_supabase] = lambda: mock_supabase
    app.dependency_overrides[get_supabase_admin] = lambda: mock_supabase
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
