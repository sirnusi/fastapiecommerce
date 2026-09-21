import pytest
import models

# def test_create_category(client):
#     response = client.post("/categories/create", json={"name": "Fashion", "slug": "fashion"})
#     assert response.status_code == 201
#     assert response.json()["slug"] == "fashion"

def test_create_duplicate_category(client, session):
    cat = models.Categories(name="Existing", slug="existing")
    session.add(cat)
    session.commit()
    
    response = client.post("/categories/create", json={"name": "Existing", "slug": "existing"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Category slug already exists"

def test_get_categories(client, session):
    session.add_all([
        models.Categories(name="Cat 1", slug="cat-1"),
        models.Categories(name="Cat 2", slug="cat-2")
    ])
    session.commit()
    
    response = client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_categories_not_found(client, session):
    response = client.get("/categories/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_update_category(client, session):
    cat = models.Categories(name="Old Name", slug="old-name")
    session.add(cat)
    session.commit()
    
    response = client.put(f"/categories/update/{cat.id}", json={"name": "New Name", "slug": "new-name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

def test_update_category_not_found(client):
    response = client.put("/categories/update/999", json={"name": "New Name", "slug": "new-name"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_delete_category(client, session):
    cat = models.Categories(name="To Delete", slug="to-delete")
    session.add(cat)
    session.commit()

    response = client.delete(f"/categories/delete/{cat.id}")
    assert response.status_code == 204

def test_delete_category_not_found(client):
    response = client.delete("/categories/delete/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"