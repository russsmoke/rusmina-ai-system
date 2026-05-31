from fastapi import FastAPI, UploadFile
import pandas as pd
import logging

from src.models.load_artifacts import load_artifacts
from src.models.predict import predict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bank Churn Prediction API")

logger.info("Загрузка артефактов...")
model, preprocessor, feature_names, shap_explainer = load_artifacts()
logger.info("Артефакты успешно загружены")


@app.get("/health")
def health():
    logger.info("Запрос /health получен")
    return {"status": "ok"}


# --- 1. Предсказание для одного клиента ---
@app.post("/predict")
def predict_one(data: dict):
    logger.info(f"Запрос /predict получен")
    try:
        df = pd.DataFrame([data])

        X = preprocessor.preprocess_for_inference(df)
        result = predict(model, X)

        prob = float(result["probabilities"][0])
        label = int(result["labels"][0])
        logger.info(f"Предсказание выполнено: вероятность={prob:.4f}, флаг={label}")

        return {
            "churn_probability": prob,
            "churn_flag": label
        }

    except Exception as e:
        logger.error(f"Ошибка предсказания: {e}")
        return {"error": str(e)}


# --- 2. Batch предсказание (CSV) ---
from fastapi.responses import StreamingResponse
import io


@app.post("/predict_batch")
async def predict_batch(file: UploadFile):
    logger.info(f"Запрос /predict_batch получен, файл: {file.filename}")
    df = pd.read_csv(file.file)
    logger.info(f"Загружено {len(df)} записей")
    X = preprocessor.preprocess_for_inference(df)

    result = predict(model, X)

    df["churn_probability"] = result["probabilities"]
    df["churn_flag"] = result["labels"]

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    logger.info(f"Batch предсказание выполнено: {len(df)} записей")

    filename = f"predictions_{len(df)}_rows.csv"
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )