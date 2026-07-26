# African Life Expectancy Predictor

## Overview

This repository contains a life expectancy prediction system for African countries using machine learning.
It includes:
- a FastAPI backend in `summative/API/prediction.py`
- model and scaler artifacts in `summative/API/`
- a Flutter frontend in `summative/flutterapp/`
- a notebook for data exploration in `summative/linear_regression/multivariate.ipynb`

## What this project does

- Loads the dataset from `Life Expectancy Data.csv`
- Filters data for African countries
- Fills missing numeric values with medians
- Encodes countries using a fitted `LabelEncoder`
- Scales features with `StandardScaler`
- Predicts life expectancy with a `RandomForestRegressor`
- Serves predictions through a FastAPI JSON endpoint
- Supports background retraining via `/retrain`

## Repository structure

```text
linear_regression_model/
├── Life Expectancy Data.csv          # Dataset used for training and retraining
├── README.md                         # Project README
├── summative/
│   ├── API/
│   │   ├── prediction.py             # FastAPI implementation
│   │   ├── best_model.joblib         # Saved model artifact
│   │   ├── scaler.joblib             # Saved scaler artifact
│   │   ├── country_encoder.joblib    # Country encoder artifact
│   │   └── requirements.txt          # API dependencies
│   ├── flutterapp/                   # Flutter mobile application
│   │   ├── lib/main.dart             # Flutter app entry point
│   │   └── pubspec.yaml              # Flutter package manifest
│   └── linear_regression/
│       └── multivariate.ipynb        # Notebook for model development
└── pyproject.toml                    # Python package metadata
```

## Quick start

### Set up the Python API

```bash
cd /home/tyler/Downloads/linear_regression_model/summative
uv venv
source .venv/bin/activate
uv pip install -r API/requirements.txt
```

### Run the API locally

```bash
cd /home/tyler/Downloads/linear_regression_model/summative/API
uvicorn prediction:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- `http://localhost:8000/docs`
- `http://localhost:8000`

### Run the Flutter app

```bash
cd /home/tyler/Downloads/linear_regression_model/summative/flutterapp
flutter pub get
flutter run
```

## API endpoints

### `GET /`
Returns the API status and docs location.

### `POST /predict`
Predicts life expectancy for a valid African country.

Example request:

```json
{
  "country": "Kenya",
  "adult_mortality": 150.5,
  "infant_deaths": 25,
  "bmi": 22.5,
  "gdp": 5000.0,
  "schooling": 10.5
}
```

Example response:

```json
{
  "country": "Kenya",
  "predicted_life_expectancy_years": 68.42,
  "status": "success"
}
```

### `POST /retrain`
Starts a background model retraining task.

Response:

```json
{
  "message": "Model retraining process started in background."
}
```

## Input validation

The API validates these input fields:
- `country`: valid African country name (case-insensitive)
- `country_code`: optional numeric country index
- `adult_mortality`: 1.0 to 1000.0
- `infant_deaths`: 0 to 1000
- `bmi`: 1.0 to 60.0
- `gdp`: 10.0 to 150000.0
- `schooling`: 0.0 to 25.0

## Model details

Features used for prediction:
- `Country_Encoded`
- `Adult Mortality`
- `infant deaths`
- `BMI`
- `GDP`
- `Schooling`

Target:
- `Life expectancy`

Artifacts loaded from:
- `summative/API/best_model.joblib`
- `summative/API/scaler.joblib`

## CORS configuration

Allowed origins:
- `https://linear-regression-model-0uwb.onrender.com`
- `http://localhost:5000`
- `http://127.0.0.1:5000`
- `http://localhost:8080`
- `http://127.0.0.1:8080`
- `http://localhost`

Allowed methods:
- GET
- POST

Allowed headers:
- `*`

Credentials:
- enabled

## Retraining process

The `/retrain` endpoint performs:
1. Load `Life Expectancy Data.csv`
2. Filter to African countries
3. Impute missing numeric values with medians
4. Encode countries using a fitted `LabelEncoder`
5. Scale features with `StandardScaler`
6. Train a `RandomForestRegressor`
7. Save updated artifacts

## Deployment notes

For deployment, use:
- `pip install -r requirements.txt`
- `uvicorn API.prediction:app --host 0.0.0.0 --port 8000`

## Notes

- `summative/API/prediction.py` contains the FastAPI service and retraining logic.
- `summative/flutterapp` contains the Flutter frontend.
- `summative/linear_regression/multivariate.ipynb` contains the analysis notebook.
- Keep `Life Expectancy Data.csv` in the repository root for `/retrain`.

## License

MIT
Link to demo video: https://youtu.be/6nSdSx18xPY

