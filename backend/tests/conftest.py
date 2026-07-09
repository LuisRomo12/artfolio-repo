import pytest
from unittest.mock import MagicMock, patch

# 1. Setup mock cursor and connection
mock_cursor = MagicMock()
mock_cursor.__enter__.return_value = mock_cursor

mock_conn = MagicMock()
mock_conn.cursor.return_value = mock_cursor
mock_conn.__enter__.return_value = mock_conn

mock_pool = MagicMock()
mock_pool.getconn.return_value = mock_conn

# 2. Patch psycopg2.pool.ThreadedConnectionPool BEFORE any app imports
patcher_pool = patch("psycopg2.pool.ThreadedConnectionPool", return_value=mock_pool)
patcher_pool.start()

# 3. Patch Cloudinary init to avoid configuration issues
patcher_cloudinary_init = patch("app.config.init_cloudinary", MagicMock())
patcher_cloudinary_init.start()

# Now import the FastAPI app and other modules
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client fixture."""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_cursor():
    """Fixture to access the mocked cursor and configure its query return values."""
    mock_cursor.reset_mock()
    # Reset all method return values and side effects to default
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchone.side_effect = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchall.side_effect = None
    mock_cursor.description = None
    return mock_cursor
