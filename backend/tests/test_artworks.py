import pytest
from datetime import datetime
from unittest.mock import patch
from app.utils.security import create_access_token

def test_get_artworks(client, db_cursor):
    """Test public list artworks endpoint."""
    db_cursor.fetchall.return_value = [
        (1, "El Lamento de Ícaro", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1200.00, "https://cloudinary/image1.jpg", "Disponible", 1, datetime.utcnow()),
        (2, "Memento Mori II", "Óleo y pan de oro", "80 x 80 cm", 2025, 950.00, "https://cloudinary/image2.jpg", "Vendida", 1, datetime.utcnow())
    ]
    
    response = client.get("/artworks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["titulo"] == "El Lamento de Ícaro"
    assert data[1]["titulo"] == "Memento Mori II"

def test_get_artworks_filtered_by_collection(client, db_cursor):
    """Test public list artworks filtered by collection_id query parameter."""
    db_cursor.fetchall.return_value = [
        (2, "Memento Mori II", "Óleo y pan de oro", "80 x 80 cm", 2025, 950.00, "https://cloudinary/image2.jpg", "Vendida", 5, datetime.utcnow())
    ]
    
    response = client.get("/artworks/?coleccion_id=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["coleccion_id"] == 5
    # Verify the SQL query checked for coleccion_id = 5
    db_cursor.execute.assert_called_with(
        "SELECT id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at FROM obras WHERE coleccion_id = %s ORDER BY created_at DESC",
        (5,)
    )

def test_get_artwork_by_id_success(client, db_cursor):
    """Test single artwork detail retrieval."""
    db_cursor.fetchone.return_value = (1, "El Lamento de Ícaro", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1200.00, "https://cloudinary/image1.jpg", "Disponible", 1, datetime.utcnow())
    
    response = client.get("/artworks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["titulo"] == "El Lamento de Ícaro"

def test_get_artwork_by_id_not_found(client, db_cursor):
    """Test artwork details not found returns 404."""
    db_cursor.fetchone.return_value = None
    
    response = client.get("/artworks/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Obra no encontrada"

@patch("app.routes.artworks.cloudinary.uploader.upload")
def test_upload_artwork_image_success(mock_upload, client, db_cursor):
    """Test image upload mock to Cloudinary CDN."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. get_current_user finds user
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())
    
    # Mock Cloudinary SDK upload response
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/demo/image/upload/v1234/artfolio/sample.png"
    }
    
    # Uploaded files
    files = {"file": ("sample.png", b"fake-binary-image-data", "image/png")}
    
    response = client.post("/artworks/upload", files=files, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/artfolio/sample.png"}
    mock_upload.assert_called_once()

def test_upload_artwork_image_invalid_extension(client, db_cursor):
    """Test upload fails with disallowed file type extension."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())
    
    files = {"file": ("document.pdf", b"fake-pdf-data", "application/pdf")}
    response = client.post("/artworks/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "Tipo de archivo no permitido" in response.json()["detail"]

def test_create_artwork_success(client, db_cursor):
    """Test protected artwork creation succeeds with valid inputs."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st fetchone: get_current_user finds user
    # 2nd fetchone: create_artwork check collection existence returns existing collection ID
    # 3rd fetchone: create_artwork RETURNING inserted row
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (5,),  # Collection exists check
        (1, "El Lamento de Ícaro", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1200.00, "https://cloudinary/image1.jpg", "Disponible", 5, datetime.utcnow())
    ]
    
    payload = {
        "titulo": "El Lamento de Ícaro",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1200.00,
        "imagen_url": "https://cloudinary/image1.jpg",
        "estado": "Disponible",
        "coleccion_id": 5
    }
    
    response = client.post("/artworks/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["titulo"] == "El Lamento de Ícaro"
    assert data["estado"] == "Disponible"

def test_create_artwork_invalid_state(client, db_cursor):
    """Test artwork creation fails when Pydantic regex pattern check fails on state."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())

    payload = {
        "titulo": "El Lamento de Ícaro",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1200.00,
        "imagen_url": "https://cloudinary/image1.jpg",
        "estado": "Vendido-Inexistente",  # Not matching ('Disponible', 'Vendida', 'En exhibición')
        "coleccion_id": 5
    }
    
    response = client.post("/artworks/", json=payload, headers=headers)
    # Fails Pydantic validation:
    assert response.status_code == 422

def test_update_artwork_success(client, db_cursor):
    """Test protected artwork update succeeds."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st: auth
    # 2nd: check artwork existence
    # 3rd: check collection existence
    # 4th: returning row
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (1,),  # Artwork found
        (5,),  # Collection found
        (1, "El Lamento de Ícaro (Editado)", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1300.00, "https://cloudinary/image1.jpg", "Disponible", 5, datetime.utcnow())
    ]
    
    payload = {
        "titulo": "El Lamento de Ícaro (Editado)",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1300.00,
        "imagen_url": "https://cloudinary/image1.jpg",
        "estado": "Disponible",
        "coleccion_id": 5
    }
    
    response = client.put("/artworks/1", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "El Lamento de Ícaro (Editado)"
    assert float(data["precio"]) == 1300.00

def test_delete_artwork_success(client, db_cursor):
    """Test protected artwork deletion succeeds."""
    token = create_access_token({"sub": "artist@artfolio.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1st: auth
    # 2nd: check artwork existence
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (1,)  # Artwork found
    ]
    
    response = client.delete("/artworks/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Obra eliminada exitosamente"}
