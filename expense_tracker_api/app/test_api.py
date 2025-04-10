import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_expense():
    payload = {
        "name": "Тестова витрата",
        "amount_uah": 100,
        "date": "2025-04-10"
        # amount_usd можна не вказувати, якщо він розраховується на сервері
    }

    response = requests.post(f"{BASE_URL}/expenses/", json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
    data = response.json()
    assert data["name"] == "Тестова витрата"
    assert data["amount_uah"] == 100
    assert "amount_usd" in data and data["amount_usd"] > 0
