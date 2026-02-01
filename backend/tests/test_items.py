from fastapi.testclient import TestClient
from backend.main import app



def test_get_items_initially_empty(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_create_item_success(client):
    response = client.post(
        "/items",
        json={
            "name": "Milk",
            "price": 50,
            "quantity": 10,
            "minimum_quantity": 5
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["item"]["name"] == "milk"
    assert data["item"]["quantity"] == 10
    assert data["item"]["low_stock"] is False


def test_sell_item_triggers_low_stock(client):
    response = client.post(
        "/sales",
        json={
            "item_name": "Milk",
            "quantity_sold": 6
        }
    )

    assert response.status_code == 200

    item = response.json()["item"]
    assert item["quantity"] == 4
    assert item["low_stock"] is True

    
def test_create_item_invalid_price(client):
    response = client.post(
        "/items",
        json={
            "name": "Bread",
            "price": -10,
            "quantity": 5,
            "minimum_quantity": 2
        }
    )

    assert response.status_code == 400
    assert "Price must be greater than 0" in response.json()["detail"]

def test_create_item_duplicate_name(client):
    # First creation
    client.post(
        "/items",
        json={
            "name": "Eggs",
            "price": 20,
            "quantity": 12,
            "minimum_quantity": 6
        }
    )

    # Duplicate creation
    response = client.post(
        "/items",
        json={
            "name": "Eggs",
            "price": 20,
            "quantity": 12,
            "minimum_quantity": 6
        }
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_sell_item_insufficient_stock(client):
    client.post(
        "/items",
        json={
            "name": "Juice",
            "price": 30,
            "quantity": 3,
            "minimum_quantity": 1
        }
    )

    response = client.post(
        "/sales",
        json={
            "item_name": "Juice",
            "quantity_sold": 5
        }
    )

    assert response.status_code == 400
    assert "Not enough stock" in response.json()["detail"]

def test_sell_item_not_found(client):
    response = client.post(
        "/sales",
        json={
            "item_name": "NonExistingItem",
            "quantity_sold": 1
        }
    )

    assert response.status_code == 404


def test_sales_history_records_sale(client):
    # Get initial sales count
    initial_response = client.get("/sales")
    initial_count = initial_response.json()["count"]

    # Create item
    client.post(
        "/items",
        json={
            "name": "Rice",
            "price": 40,
            "quantity": 10,
            "minimum_quantity": 3
        }
    )

    # Make a sale
    client.post(
        "/sales",
        json={
            "item_name": "Rice",
            "quantity_sold": 2
        }
    )

    # Get sales history again
    response = client.get("/sales")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == initial_count + 1

    sale = data["sales"][-1]  # last sale
    assert sale["item_name"] == "rice"
    assert sale["quantity_sold"] == 2
    assert sale["price_at_sale"] == 40
    assert sale["sold_at"] is not None


def test_sales_history_multiple_sales(client):
    initial_count = client.get("/sales").json()["count"]

    # Create item
    client.post(
        "/items",
        json={
            "name": "Soap",
            "price": 25,
            "quantity": 20,
            "minimum_quantity": 5
        }
    )

    # Two sales
    client.post("/sales", json={"item_name": "Soap", "quantity_sold": 3})
    client.post("/sales", json={"item_name": "Soap", "quantity_sold": 2})

    response = client.get("/sales")
    data = response.json()

    assert data["count"] == initial_count + 2

    last_two = data["sales"][-2:]
    quantities = [sale["quantity_sold"] for sale in last_two]
    assert quantities == [3, 2]

def test_negative_minimum_quantity(client):
    response = client.post(
        "/items",
        json={
            "name": "BadItem",
            "price": 10,
            "quantity": 1,
            "minimum_quantity": -1
        }
    )
    assert response.status_code == 422

def test_sell_item_oversell_returns_409(client):
    response = client.post(
        "/sales",
        json={"item_name": "Milk", "quantity_sold": 999}
    )
    assert response.status_code == 409