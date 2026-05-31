FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Говорим Docker: "контейнер слушает порт 8000" (документация)

CMD ["uvicorn", "src.service.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Команда запуска сервиса при старте контейнера
# src.service:app = файл src/service.py, объект app = FastAPI()