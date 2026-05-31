from fastapi.testclient import TestClient
from src.service.main import app

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
    assert "model" in r.json()


def test_predict_returns_fields():
    """Тест, что эндпоинт /predict возвращает нужные поля"""
    r = client.post("/predict", json=sample_customer)
    assert r.status_code == 200
    assert "churn_probability" in r.json()  # или "churn_proba"
    assert "churn_flag" in r.json()  # или "at_risk"


def test_predict_proba_range():
    """Тест, что вероятность в диапазоне [0, 1]"""
    r = client.post("/predict", json=sample_customer)
    assert r.status_code == 200
    
    proba = r.json().get("churn_probability")
    assert proba is not None
    assert 0 <= proba <= 1


def test_predict_with_different_customers():
    """Тест для разных типов клиентов"""
    # Клиент с высоким риском
    high_risk = {
        "CreditScore": 400,
        "Age": 60,
        "Tenure": 1,
        "Balance": 200000,
        "NumOfProducts": 1,
        "HasCrCard": 0,
        "IsActiveMember": 0,
        "EstimatedSalary": 20000,
        "Geography": "Germany",
        "Gender": "Female"
    }
    
    # Клиент с низким риском
    low_risk = {
        "CreditScore": 800,
        "Age": 25,
        "Tenure": 8,
        "Balance": 10000,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 100000,
        "Geography": "France",
        "Gender": "Male"
    }
    
    r_high = client.post("/predict", json=high_risk)
    r_low = client.post("/predict", json=low_risk)
    
    assert r_high.status_code == 200
    assert r_low.status_code == 200
    
    proba_high = r_high.json().get("churn_probability")
    proba_low = r_low.json().get("churn_probability")
    
    # Вероятность оттока должна быть выше у high_risk клиента
    assert proba_high > proba_low


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