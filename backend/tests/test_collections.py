import pytest
from datetime import datetime
from app.utils.security import create_access_token

def test_get_collections(client, db_cursor):
    """Test public list collections endpoint."""
    # Mock database returns two collections
    db_cursor.fetchall.return_value = [
        (1, "Mitologías Perdidas", "Descripción de mitos", datetime.utcnow()),
        (2, "Anatomía de la Melancolía", "Estudios anatómicos", datetime.utcnow())
    ]
    
    response = client.get("/collections/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Mitologías Perdidas"
    assert data[1]["nombre"] == "Anatomía de la Melancolía"

def test_get_collection_by_id_success(client, db_cursor):
    """Test retrieving details of a single collection by ID."""
    db_cursor.fetchone.return_value = (1, "Mitologías Perdidas", "Descripción de mitos", datetime.utcnow())
    
    response = client.get("/collections/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["nombre"] == "Mitologías Perdidas"

def test_get_collection_by_id_not_found(client, db_cursor):
    """Test collection not found returns 404."""
    db_cursor.fetchone.return_value = None
    
    response = client.get("/collections/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Colección no encontrada"

def test_create_collection_unauthorized(client):
    """Test protected create collection fails without Authorization header."""
    payload = {
        "nombre": "Nueva Colección",
        "descripcion": "Una descripción de prueba"
    }
    response = client.post("/collections/", json=payload)
    assert response.status_code == 401  # Unauthorized (FastAPI HTTPBearer dependency default on missing header)

def test_create_collection_success(client, db_cursor):
    """Test protected collection creation succeeds with valid JWT."""
    # Generate token
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st fetchone: get_current_user finds user
    # 2nd fetchone: create_collection returns new collection
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10, "Nueva Colección", "Una descripción de prueba", datetime.utcnow())
    ]
    
    payload = {
        "nombre": "Nueva Colección",
        "descripcion": "Una descripción de prueba"
    }
    response = client.post("/collections/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 10
    assert data["nombre"] == "Nueva Colección"

def test_update_collection_success(client, db_cursor):
    """Test protected collection update succeeds."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st fetchone: get_current_user finds user
    # 2nd fetchone: update_collection check existence returns existing
    # 3rd fetchone: update_collection returning updated collection row
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10,),  # Check existence: found
        (10, "Colección Editada", "Descripción editada", datetime.utcnow())
    ]
    
    payload = {
        "nombre": "Colección Editada",
        "descripcion": "Descripción editada"
    }
    response = client.put("/collections/10", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["nombre"] == "Colección Editada"

def test_delete_collection_success(client, db_cursor):
    """Test protected collection deletion succeeds."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st fetchone: get_current_user finds user
    # 2nd fetchone: delete_collection check existence returns existing
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10,)  # Check existence: found
    ]
    
    response = client.delete("/collections/10", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Colección eliminada exitosamente"}
