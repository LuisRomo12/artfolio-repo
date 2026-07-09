import pytest
from datetime import datetime
from app.utils.security import get_password_hash

def test_register_success(client, db_cursor):
    """Test successful user registration."""
    # 1. Mock select query to return None (no user exists with this email)
    # 2. Mock insert query RETURNING statement to return the new user details
    db_cursor.fetchone.side_effect = [
        None,  # Check user existence: not found
        (1, "test_artist@artfolio.com", datetime.utcnow())  # Insert statement return value
    ]

    payload = {
        "email": "test_artist@artfolio.com",
        "password": "securepassword123"
    }
    
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "test_artist@artfolio.com"
    assert "created_at" in data

def test_register_password_too_short(client):
    """Test register fails when password is less than 8 characters."""
    payload = {
        "email": "test_artist@artfolio.com",
        "password": "short"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation)

def test_register_user_already_exists(client, db_cursor):
    """Test register fails when email is already registered."""
    # Mock select query to return a mock row (user exists)
    db_cursor.fetchone.return_value = (1,)

    payload = {
        "email": "existing_artist@artfolio.com",
        "password": "securepassword123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "El correo electrónico ya está registrado"

def test_login_success(client, db_cursor):
    """Test successful login returns a JWT access token."""
    raw_password = "artista_password_123"
    hashed_password = get_password_hash(raw_password)
    
    # Mock select query during login to return (id, email, password_hash)
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", hashed_password)

    payload = {
        "email": "artist@artfolio.com",
        "password": raw_password
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, db_cursor):
    """Test login fails with incorrect password or non-existing email."""
    # Case 1: User does not exist (returns None)
    db_cursor.fetchone.return_value = None

    payload = {
        "email": "unknown@artfolio.com",
        "password": "some_password"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"
