import os
from pathlib import Path
from typing import Literal
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ==============================================================================
# 1. LIST OF VALID AFRICAN COUNTRIES
# ==============================================================================
AFRICAN_COUNTRIES_TUPLE = (
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', "Cote d'Ivoire",
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea',
    'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho',
    'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco',
    'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe',
    'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan',
    'Sudan', 'Swaziland', 'Togo', 'Tunisia', 'Uganda', 'United Republic of Tanzania',
    'Zambia', 'Zimbabwe'
)

# Define Type for Pydantic string validation
AfricanCountry = Literal[
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', "Cote d'Ivoire",
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea',
    'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho',
    'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco',
    'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe',
    'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan',
    'Sudan', 'Swaziland', 'Togo', 'Tunisia', 'Uganda', 'United Republic of Tanzania',
    'Zambia', 'Zimbabwe'
]

# Build fitted LabelEncoder matching training alphabetization
le_country = LabelEncoder()
le_country.fit(sorted(list(AFRICAN_COUNTRIES_TUPLE)))

# 2. FASTAPI APP INITIALIZATION

app = FastAPI(
    title="African Life Expectancy Predictor API",
    description="API for predicting life expectancy across African nations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

ALLOWED_ORIGINS = [
    "https://linear-regression-model-0uwb.onrender.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 3. PYDANTIC INPUT SCHEMA (STRICT COUNTRY STRING VALIDATION)

class LifeExpectancyInput(BaseModel):
    country: AfricanCountry = Field(..., description="Must be a valid African country name string")
    adult_mortality: float = Field(..., ge=1.0, le=1000.0, description="Adult Mortality rate per 1000 population")
    infant_deaths: int = Field(..., ge=0, le=1000, description="Number of Infant Deaths per 1000 population")
    bmi: float = Field(..., ge=1.0, le=60.0, description="Average BMI of population")
    gdp: float = Field(..., ge=10.0, le=150000.0, description="GDP per capita in USD")
    schooling: float = Field(..., ge=0.0, le=25.0, description="Average years of schooling")


# 4. PATH RESOLUTION & ARTIFACT SETUP

API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parents[1] if len(API_DIR.parents) >= 2 else API_DIR.parent

MODEL_PATH = API_DIR / "best_model.joblib"
SCALER_PATH = API_DIR / "scaler.joblib"
DATA_PATH = PROJECT_ROOT / "Life Expectancy Data.csv"

FEATURES = ["Country_Encoded", "Adult Mortality", "infant deaths", "BMI", "GDP", "Schooling"]
TARGET = "Life expectancy"

def load_artifacts():
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    scaler = joblib.load(SCALER_PATH) if SCALER_PATH.exists() else None
    return model, scaler

model, scaler = load_artifacts()


# 5. ENDPOINTS

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "African Life Expectancy API Active", "docs": "/docs"}

@app.post("/predict", status_code=status.HTTP_200_OK)
def predict_life_expectancy(data: LifeExpectancyInput):
    global model, scaler
    if model is None or scaler is None:
        model, scaler = load_artifacts()
        if model is None or scaler is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model or scaler artifacts missing on server."
            )

    # Encode string country to integer code
    try:
        encoded_country = int(le_country.transform([data.country])[0])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid country '{data.country}'. Must be a recognized African nation."
        )

    # DataFrame formatted for feature scaling
    input_df = pd.DataFrame([{
        "Country_Encoded": encoded_country,
        "Adult Mortality": data.adult_mortality,
        "infant deaths": data.infant_deaths,
        "BMI": data.bmi,
        "GDP": data.gdp,
        "Schooling": data.schooling,
    }])[FEATURES]

    scaled_features = scaler.transform(input_df)
    prediction = model.predict(scaled_features)

    return {
        "country": data.country,
        "predicted_life_expectancy_years": round(float(prediction[0]), 2),
        "status": "success",
    }


# 6. RETRAINING TASK

def execute_model_retraining():
    global model, scaler
    try:
        if not DATA_PATH.exists():
            print(f"[Warning] Dataset not found at {DATA_PATH}")
            return

        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()
        africa_df = df[df["Country"].isin(AFRICAN_COUNTRIES_TUPLE)].copy()

        numeric_cols = ["Life expectancy", "Adult Mortality", "infant deaths", "BMI", "GDP", "Schooling"]
        for col in numeric_cols:
            if africa_df[col].isnull().sum() > 0:
                africa_df[col] = africa_df[col].fillna(africa_df[col].median())

        africa_df["Country_Encoded"] = le_country.transform(africa_df["Country"])

        X = africa_df[FEATURES]
        y = africa_df[TARGET]

        new_scaler = StandardScaler()
        X_scaled = new_scaler.fit_transform(X)

        new_model = RandomForestRegressor(n_estimators=100, random_state=42)
        new_model.fit(X_scaled, y)

        joblib.dump(new_model, MODEL_PATH)
        joblib.dump(new_scaler, SCALER_PATH)

        model, scaler = new_model, new_scaler
        print("[Success] Background retraining finished!")
    except Exception as e:
        print(f"[Error] Retraining failed: {str(e)}")

@app.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_model_retraining)
    return {"message": "Model retraining process started in background."}