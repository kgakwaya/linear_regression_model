import os
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Initialize FastAPI App
app = FastAPI(
    title="African Life Expectancy Predictor API",
    description="API for predicting African nation life expectancy based on health and socioeconomic indicators.",
    version="1.0.0"
)

# ------------------------------------------------------------------
# CORS Configuration
# Allowed origins restricted for security compliance (not using wildcard *)
# ------------------------------------------------------------------
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "https://*.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Pydantic Input Schema with Strict Range Constraints
# ------------------------------------------------------------------
class LifeExpectancyInput(BaseModel):
    adult_mortality: float = Field(..., ge=1.0, le=1000.0, description="Adult Mortality rate per 1000 population")
    infant_deaths: int = Field(..., ge=0, le=1000, description="Number of Infant Deaths per 1000 population")
    bmi: float = Field(..., ge=1.0, le=60.0, description="Average BMI of population")
    gdp: float = Field(..., ge=10.0, le=150000.0, description="GDP per capita in USD")
    schooling: float = Field(..., ge=0.0, le=25.0, description="Average years of schooling")

# ------------------------------------------------------------------
# Load Model Artifacts
# ------------------------------------------------------------------
MODEL_PATH = "best_model.joblib"
SCALER_PATH = "scaler.joblib"

def load_artifacts():
    model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
    scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
    return model, scaler

model, scaler = load_artifacts()

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {
        "message": "African Life Expectancy Prediction API is active.",
        "documentation": "/docs"
    }

# ------------------------------------------------------------------
# Prediction Endpoint
# ------------------------------------------------------------------
@app.post("/predict", status_code=status.HTTP_200_OK)
def predict_life_expectancy(data: LifeExpectancyInput):
    global model, scaler
    if model is None or scaler is None:
        model, scaler = load_artifacts()
        if model is None or scaler is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model or scaler artifacts are missing on server."
            )
    
    # Structure features into DataFrame matching training feature order
    input_data = pd.DataFrame([{
        'Adult Mortality': data.adult_mortality,
        'infant deaths': data.infant_deaths,
        'BMI': data.bmi,
        'GDP': data.gdp,
        'Schooling': data.schooling
    }])

    # Transform data and make prediction
    scaled_features = scaler.transform(input_data)
    prediction = model.predict(scaled_features)

    return {
        "predicted_life_expectancy_years": round(float(prediction[0]), 2),
        "status": "success"
    }

# ------------------------------------------------------------------
# Background Task & Retraining Trigger Endpoint
# ------------------------------------------------------------------
def execute_model_retraining():
    """Background execution to reload data and update model artifacts."""
    global model, scaler
    if os.path.exists("Life Expectancy Data.csv"):
        df = pd.read_csv("Life Expectancy Data.csv")
        df.columns = df.columns.str.strip()
        
        african_countries = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Kenya', 'Rwanda', 'Nigeria', 'Ghana', 'South Africa', 'Uganda', 'Tanzania']
        africa_df = df[df['Country'].isin(african_countries)].copy()
        
        features = ['Adult Mortality', 'infant deaths', 'BMI', 'GDP', 'Schooling']
        dataset = africa_df[features + ['Life expectancy']].fillna(africa_df.median(numeric_only=True))
        
        X = dataset[features]
        y = dataset['Life expectancy']
        
        new_scaler = StandardScaler()
        X_scaled = new_scaler.fit_transform(X)
        
        new_model = RandomForestRegressor(n_estimators=100, random_state=42)
        new_model.fit(X_scaled, y)
        
        joblib.dump(new_model, MODEL_PATH)
        joblib.dump(new_scaler, SCALER_PATH)
        
        model, scaler = new_model, new_scaler
        print("Model retraining completed successfully!")

@app.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_model_retraining)
    return {"message": "Model retraining process started in background."}