from fastapi.testclient import TestClient
from src.service.main import app
import pytest
client = TestClient(app)

# Пример данных клиента
sample_customer = {
    "CreditScore": 650,
    "Age": 35,
    "Tenure": 5,
    "Balance": 50000,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000,
    "Geography": "France",
    "Gender": "Male"
}

def test_health():
    """Тест эндпоинта health"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_missing_field():
    """Тест на отсутствие обязательного поля"""
    incomplete_data = {
        "CreditScore": 650,
        "Age": 35,
        # отсутствует Tenure, Balance и др.
    }
    r = client.post("/predict", json=incomplete_data)
    # Должна быть ошибка 422 (Validation Error) или 500
    assert r.status_code in [422, 500]


def test_predict_invalid_value():
    """Тест на некорректное значение"""
    invalid_data = {
        "CreditScore": 1000,  # невалидный CreditScore (макс 850)
        "Age": 35,
        "Tenure": 5,
        "Balance": 50000,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 50000,
        "Geography": "France",
        "Gender": "Male"
    }
    r = client.post("/predict", json=invalid_data)
    # Должна быть ошибка валидации
    assert r.status_code == 422


def test_predict_batch():
    """Тест batch эндпоинта"""
    import io
    import pandas as pd
    
    # Создаём тестовый CSV
    df = pd.DataFrame([sample_customer, sample_customer])
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Отправляем файл
    files = {"file": ("test.csv", csv_buffer.getvalue(), "text/csv")}
    r = client.post("/predict_batch", files=files)
    
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")