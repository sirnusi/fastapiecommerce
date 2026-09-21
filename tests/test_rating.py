import pytest
import models


@pytest.fixture
def setup_product(session):
    cat = models.Categories(name="Home", slug="home")
    session.add(cat)
    session.commit()
    
    prod = models.Product(name="Lamp", slug="lamp", price=15.00, category_id=cat.id)
    session.add(prod)
    session.commit()
    return prod

def test_create_rating(client, setup_product):
    response = client.post(
        "/ratings/create",
        json={"rating": 4.0, "description": "Good", "product_id": setup_product.id}
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == 1


def test_get_product_ratings(client, setup_product):
    # 1. Capture the response for the creation request
    create_response = client.post(
        "/ratings/create",
        json={"rating": 5.0, "description": "Excellent", "product_id": setup_product.id}
    )
    
    # 2. Print the error and assert success to prevent silent failures
    print("Creation response:", create_response.json())
    assert create_response.status_code == 201, "Rating creation failed"
    
    # 3. Proceed with the GET request
    response = client.get(f"/ratings/product/{setup_product.id}")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_delete_rating(client, session, setup_product):
    # Create a rating first
    rating = models.Rating(rating=5.0, description="Great", product_id=setup_product.id, user_id=1)
    session.add(rating)
    session.commit()
    
    response = client.delete(f"/ratings/delete/{rating.id}")
    assert response.status_code == 204
    
    # Verify the rating is marked as inactive
    session.refresh(rating)
    assert not rating.is_active

def test_delete_rating_not_found(client):
    response = client.delete("/ratings/delete/9999")
    assert response.status_code == 404

def test_delete_rating_unauthorized(client, session, setup_product):
    # Rating belongs to user 2, client fixture acts as user 1
    rating = models.Rating(rating=5.0, description="Great", product_id=setup_product.id, user_id=2)
    session.add(rating)
    session.commit()
    
    response = client.delete(f"/ratings/delete/{rating.id}")
    assert response.status_code == 403