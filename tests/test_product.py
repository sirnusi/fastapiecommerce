from fastapi import FastAPI
import pytest
from routers.auth import get_current_user
import models

app = FastAPI() 

@pytest.fixture
def setup_category(session):
    category = models.Categories(name="Tech", slug="tech")
    session.add(category)
    session.commit()
    return category

def test_create_product(client, setup_category):
    response = client.post(
        "/products/create-product",
        json={
            "name": "Mouse",
            "slug": "mouse",
            "price": 25.00,
            "stock_quantity": 10,
            "is_active": True,
            "category_id": setup_category.id
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Mouse"

def test_get_product(client, session, setup_category):
    product = models.Product(name="Keyboard", slug="kb", price=50.00, stock_quantity=5, category_id=setup_category.id)
    session.add(product)
    session.commit()
    
    response = client.get(f"/products/{product.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Keyboard"

def test_get_nonexistent_product(client):
    response = client.get("/products/999")
    assert response.status_code == 404

def test_update_product(client, session, setup_category):
    product = models.Product(name="Monitor", slug="monitor", price=150.00, stock_quantity=3, category_id=setup_category.id)
    session.add(product)
    session.commit()
    
    response = client.patch(
        f"/products/patch-product/{product.id}",
        json={
            "name": "Monitor",        # Required
            "slug": "monitor",        # Required
            "price": "140.00",        # Updated (use string for Decimal)
            "stock_quantity": 4,      # Updated
            "category_id": setup_category.id # Required
        }
    )
    assert response.status_code == 204
    session.refresh(product)

    assert product.price == 140.00
    assert product.stock_quantity == 4
   
  
def test_update_product_not_found(client):
    response = client.patch(
        "/products/patch-product/999",
        json={"price": 100.00}
    )
    assert response.status_code == 404



def test_delete_product(client, session, setup_category):
    product = models.Product(name="Keyboard", slug="kb", price=50.00, category_id=setup_category.id)
    session.add(product)
    session.commit()
    
    response = client.delete(f"/products/delete-product/{product.id}")
    assert response.status_code == 200
    
    deleted_product = session.query(models.Product).filter(models.Product.id == product.id).first()
    assert deleted_product.is_active is False

def test_delete_product_not_found(client):
    response = client.delete("/products/delete-product/999")
    assert response.status_code == 404