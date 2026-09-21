import pytest
import models

@pytest.fixture
def setup_product(session):
    cat = models.Categories(name="Books", slug="books")
    session.add(cat)
    session.commit()
    
    prod = models.Product(name="FastAPI Guide", slug="fastapi", price=30.00, stock_quantity=5, category_id=cat.id)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod

# def test_create_order_success(client, session, setup_product):
#     response = client.post(
#         "/orders/create-order",
#         json={"items": [{"product_id": setup_product.id, "quantity": 2}]}
#     )
#     print(response.json())
#     assert response.status_code == 201
#     data = response.json()
#     assert data["total_amount"] == "60.00"
    
#     # Verify stock was deducted
#     session.refresh(setup_product)
#     assert setup_product.stock_quantity == 3

# def test_create_order_insufficient_stock(client, setup_product):
#     response = client.post(
#         "/orders/create-order",
#         json={"items": [{"product_id": setup_product.id, "quantity": 10}]}
#     )
#     assert response.status_code == 400
#     assert "Insufficient stock" in response.json()["detail"]

# def test_cancel_order_restores_stock(client, session, setup_product):
#     # 1. Capture the response and ensure the URL matches your router exactly
#     # (Change to "/orders/" if your router uses @router.post("/"))
#     response = client.post(
#         "/orders/create-order", 
#         json={"items": [{"product_id": setup_product.id, "quantity": 1}]}
#     )
    
#     # 2. ADD THIS ASSERTION to prevent silent failures
#     assert response.status_code == 201, f"Order creation failed: {response.json()}"
    
#     # 3. Verify stock was deducted
#     session.refresh(setup_product)
#     assert setup_product.stock_quantity == 4
    
#     # 4. Continue with the cancel order logic...
#     order = session.query(models.Order).first()
    
#     cancel_response = client.delete(f"/orders/{order.id}")
#     assert cancel_response.status_code == 204
    
#     # Verify stock restored
#     session.refresh(setup_product)
#     assert setup_product.stock_quantity == 5


# def test_get_user_orders(client, session, setup_product):
#     order = models.Order(user_id=1, status=models.OrderStatus.PENDING, total_amount=30.00)
#     session.add(order)
#     session.commit()
    
#     response = client.get("/orders/")
#     assert response.status_code == 200
#     assert len(response.json()) == 1
#     assert response.json()[0]["user_id"] == 1

# def test_get_order_not_found(client):
#     response = client.get("/orders/999")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Order not found"

# def test_get_order_not_authorized(client, session, setup_product):
#     # Create an order for a different user
#     order = models.Order(user_id=2, status=models.OrderStatus.PENDING, total_amount=30.00)
#     session.add(order)
#     session.commit()
    
#     response = client.get(f"/orders/{order.id}")
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Not authorized to view this order"


def test_update_order_status(client, session, setup_product):
    order = models.Order(user_id=1, status=models.OrderStatus.PENDING, total_amount=30.00)
    session.add(order)
    session.commit()

    # FIX: Remove "?status_update=shipped" from the URL. 
    # Let the router read it directly from the json payload.
    response = client.patch(
        f"/orders/{order.id}/status", 
        json={"status": "shipped"}  # Ensure the payload matches the expected schema
    )
    
    print(response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


def test_update_order_status_not_found(client):
    response = client.patch("/orders/999/status", json={"status": "shipped"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_update_order_status_not_authorized(client, session, setup_product):
    # Create an order for a different user
    order = models.Order(user_id=2, status=models.OrderStatus.PENDING, total_amount=30.00)
    session.add(order)
    session.commit()
    
    response = client.patch(f"/orders/{order.id}/status", json={"status": "shipped"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this order"

def test_update_order_status_invalid_status(client, session, setup_product):
    order = models.Order(user_id=1, status=models.OrderStatus.PENDING, total_amount=30.00)
    session.add(order)
    session.commit()
    
    response = client.patch(f"/orders/{order.id}/status", json={"status": "invalid_status"})
    assert response.status_code == 422  # Unprocessable Entity for invalid enum


def test_delete_order(client, session, setup_product):
    order = models.Order(user_id=1, status=models.OrderStatus.PENDING, total_amount=30.00)
    session.add(order)
    session.commit()

    response = client.delete(f"/orders/delete/{order.id}")
    assert response.status_code == 204
    

   
def test_delete_order_not_found(client):
    response = client.delete("/orders/delete/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"