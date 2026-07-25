import os
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ==============================================================================
# 1. FASTAPI APP INITIALIZATION
# ==============================================================================
app = FastAPI(
    title="African Life Expectancy Predictor API",
    description="API for predicting life expectancy across African nations and triggering background model retraining.",
    version="1.0.0",
    docs_url="/docs",  # Public Swagger UI endpoint
    redoc_url="/redoc"
)

# ==============================================================================
# 2. CORS MIDDLEWARE CONFIGURATION & SECURITY REASONING
# ==============================================================================
"""
CORS SECURITY REASONING:
- allow_origins: Explicitly restricted to trusted domains (Render deployment, local dev ports).
  Wildcards ("*") are strictly avoided for origins to prevent cross-site request forgery (CSRF) 
  and unauthorized API abuse from third-party sites.
- allow_credentials: Set to True to allow authenticated headers and secure sessions across domains.
- allow_methods: Strictly limited to GET and POST requests required by standard client-server communication.
- allow_headers: Permitted standard headers including Content-Type and Authorization.
"""
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

# ==============================================================================
# 3. PYDANTIC INPUT SCHEMA WITH DATA TYPES & RANGE CONSTRAINTS
# ==============================================================================
class LifeExpectancyInput(BaseModel):
    country_code: int = Field(..., ge=0, le=60, description="Encoded integer index of African Country")
    adult_mortality: float = Field(..., ge=1.0, le=1000.0, description="Adult Mortality rate per 1000 population")
    infant_deaths: int = Field(..., ge=0, le=1000, description="Number of Infant Deaths per 1000 population")
    bmi: float = Field(..., ge=1.0, le=60.0, description="Average BMI of population")
    gdp: float = Field(..., ge=10.0, le=150000.0, description="GDP per capita in USD")
    schooling: float = Field(..., ge=0.0, le=25.0, description="Average years of schooling")

# ==============================================================================
# 4. PATH RESOLUTION & MODEL ARTIFACT SETUP
# ==============================================================================
API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parents[1] if len(API_DIR.parents) >= 2 else API_DIR.parent

MODEL_PATH = API_DIR / "best_model.joblib"
SCALER_PATH = API_DIR / "scaler.joblib"
DATA_PATH = PROJECT_ROOT / "Life Expectancy Data.csv"

FEATURES = ["Country_Encoded", "Adult Mortality", "infant deaths", "BMI", "GDP", "Schooling"]
TARGET = "Life expectancy"

AFRICAN_COUNTRIES = [
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

def load_artifacts():
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    scaler = joblib.load(SCALER_PATH) if SCALER_PATH.exists() else None
    return model, scaler

model, scaler = load_artifacts()

# ==============================================================================
# 5. API ENDPOINTS
# ==============================================================================
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {
        "message": "African Life Expectancy Prediction API is active.",
        "documentation": "/docs"
    }

@app.post("/predict", status_code=status.HTTP_200_OK)
def predict_life_expectancy(data: LifeExpectancyInput):
    global model, scaler
    if model is None or scaler is None:
        model, scaler = load_artifacts()
        if model is None or scaler is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model artifacts missing on server. Run training notebook first."
            )

    # Format dataframe to match exact feature column order used during model fitting
    input_df = pd.DataFrame([{
        "Country_Encoded": data.country_code,
        "Adult Mortality": data.adult_mortality,
        "infant deaths": data.infant_deaths,
        "BMI": data.bmi,
        "GDP": data.gdp,
        "Schooling": data.schooling,
    }])[FEATURES]

    # Standardize input features using fitted scaler
    scaled_features = scaler.transform(input_df)
    prediction = model.predict(scaled_features)

    return {
        "predicted_life_expectancy_years": round(float(prediction[0]), 2),
        "status": "success",
    }

# ==============================================================================
# 6. MODEL RETRAINING BACKGROUND TASK
# ==============================================================================
def execute_model_retraining():
    global model, scaler
    try:
        if not DATA_PATH.exists():
            print(f"[Retraining Warning] Dataset not found at {DATA_PATH}. Skipping retraining.")
            return

        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()
        
        # Filter for African nations
        africa_df = df[df["Country"].isin(AFRICAN_COUNTRIES)].copy()

        # Handle missing values using median imputation
        numeric_cols = ["Life expectancy", "Adult Mortality", "infant deaths", "BMI", "GDP", "Schooling"]
        for col in numeric_cols:
            if africa_df[col].isnull().sum() > 0:
                africa_df[col] = africa_df[col].fillna(africa_df[col].median())

        # Encode categorical country feature
        le_country = LabelEncoder()
        africa_df["Country_Encoded"] = le_country.fit_transform(africa_df["Country"])

        X = africa_df[FEATURES]
        y = africa_df[TARGET]

        # Refit Scaler and Model
        new_scaler = StandardScaler()
        X_scaled = new_scaler.fit_transform(X)

        new_model = RandomForestRegressor(n_estimators=100, random_state=42)
        new_model.fit(X_scaled, y)

        # Save artifacts back to disk
        joblib.dump(new_model, MODEL_PATH)
        joblib.dump(new_scaler, SCALER_PATH)

        # Update in-memory models
        model, scaler = new_model, new_scaler
        print("[Retraining Success] Model and scaler updated successfully!")

    except Exception as e:
        print(f"[Retraining Error] Failed to complete model update: {str(e)}")

@app.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_model_retraining)
    return {"message": "Model retraining process started in background."}