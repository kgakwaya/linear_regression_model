import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

app = FastAPI(
    title="African Life Expectancy Predictor API",
    description="API for predicting life expectancy across African nations.",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    "https://linear-regression-model-0uwb.onrender.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class LifeExpectancyInput(BaseModel):
    adult_mortality: float = Field(..., ge=1.0, le=1000.0, description="Adult Mortality rate per 1000 population")
    infant_deaths: int = Field(..., ge=0, le=1000, description="Number of Infant Deaths per 1000 population")
    bmi: float = Field(..., ge=1.0, le=60.0, description="Average BMI of population")
    gdp: float = Field(..., ge=10.0, le=150000.0, description="GDP per capita in USD")
    schooling: float = Field(..., ge=0.0, le=25.0, description="Average years of schooling")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_DIR = Path(__file__).resolve().parent
MODEL_PATH = API_DIR / "best_model.joblib"
SCALER_PATH = API_DIR / "scaler.joblib"
FEATURE_ORDER_PATH = API_DIR / "feature_order.joblib"
DATA_PATH = PROJECT_ROOT / "Life Expectancy Data.csv"
FEATURES = ["Adult Mortality", "infant deaths", "BMI", "GDP", "Schooling"]
TARGET = "Life expectancy"
AFRICAN_COUNTRIES = [
    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "Burkina Faso",
    "Kenya",
    "Rwanda",
    "Nigeria",
    "Ghana",
    "South Africa",
    "Uganda",
    "Tanzania",
]


def load_artifacts():
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    scaler = joblib.load(SCALER_PATH) if SCALER_PATH.exists() else None
    return model, scaler


model, scaler = load_artifacts()


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "African Life Expectancy Prediction API is active.", "docs": "/docs"}


@app.post("/predict", status_code=status.HTTP_200_OK)
def predict_life_expectancy(data: LifeExpectancyInput):
    global model, scaler
    if model is None or scaler is None:
        model, scaler = load_artifacts()
        if model is None or scaler is None:
            raise HTTPException(status_code=500, detail="Model artifacts missing.")

    input_data = pd.DataFrame([
        {
            "Adult Mortality": data.adult_mortality,
            "infant deaths": data.infant_deaths,
            "BMI": data.bmi,
            "GDP": data.gdp,
            "Schooling": data.schooling,
        }
    ])[FEATURES]

    scaled_features = scaler.transform(input_data)
    prediction = model.predict(scaled_features)

    return {
        "predicted_life_expectancy_years": round(float(prediction[0]), 2),
        "status": "success",
    }


def execute_model_retraining():
    global model, scaler
    if not DATA_PATH.exists():
        raise FileNotFoundError("Training dataset not found.")

    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    africa_df = df[df["Country"].isin(AFRICAN_COUNTRIES)].copy()

    dataset = africa_df[FEATURES + [TARGET]].fillna(africa_df.median(numeric_only=True))
    X = dataset[FEATURES]
    y = dataset[TARGET]

    new_scaler = StandardScaler()
    X_scaled = new_scaler.fit_transform(X)

    new_model = RandomForestRegressor(n_estimators=100, random_state=42)
    new_model.fit(X_scaled, y)

    joblib.dump(new_model, MODEL_PATH)
    joblib.dump(new_scaler, SCALER_PATH)
    joblib.dump(FEATURES, FEATURE_ORDER_PATH)
    model, scaler = new_model, new_scaler


@app.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_model_retraining)
    return {"message": "Model retraining started in background."}