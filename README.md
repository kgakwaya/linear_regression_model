# African Life Expectancy Predictor

## Mission & Use Case

This project implements a **machine learning model to predict life expectancy in African nations** based on health and socioeconomic indicators. The model compares multiple regression algorithms (Linear Regression, Random Forest, and Decision Trees) to identify the best performing approach for this specific use case.



## Dataset

**Source:** World Health Organization (WHO) Life Expectancy Dataset  
**Downloaded from:** Kaggle  
**Dataset Link:** https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who

**Dataset Characteristics:**
- **Size:** 2,938 records across 193 countries (2000-2015)
- **Features Used:**
  - `Adult Mortality`: Adult mortality rate per 1000 population
  - `Infant Deaths`: Number of infant deaths per 1000 live births
  - `BMI`: Average Body Mass Index of the population
  - `GDP`: Gross Domestic Product per capita (USD)
  - `Schooling`: Average years of schooling (education level)
- **Target Variable:** `Life Expectancy`: Life expectancy in years
- **African Countries:** 12 nations selected (Algeria, Angola, Benin, Botswana, Burkina Faso, Kenya, Rwanda, Nigeria, Ghana, South Africa, Uganda, Tanzania)

**Data Quality:**
- Missing values imputed using median values for each feature
- Outliers retained to preserve realistic variance in the data
- Standardized using StandardScaler for model training

---

## Model Development & Comparison

### Algorithms Implemented:
1. **Linear Regression** (Stochastic & OLS)
2. **Random Forest Regressor** (Ensemble method)
3. **Decision Tree Regressor**

### Performance Metrics (Loss - Mean Squared Error):
| Model | MSE | RMSE | R² Score |
|-------|-----|------|----------|
| Linear Regression | 35.63 | 5.97 | 0.447 |
| Stochastic Gradient Descent (SGD) | 35.62 | 5.97 | 0.448 |
| Decision Tree | 10.71 | 3.27 | 0.834 |
| **Random Forest** (BEST) | **6.94** | **2.63** | **0.892** |

**Best Model:** Random Forest Regressor - Selected based on lowest MSE (6.94) and highest R² score (0.892)
- Explains 89.24% of the variance in life expectancy
- Average prediction error of ±2.63 years
- Ensemble method captures complex non-linear relationships better than linear models

---

## Key Visualizations

### 1. Correlation Heatmap
Shows relationships between all features and target variable. Helps identify which socioeconomic/health factors have strongest linear relationships with life expectancy.

### 2. Feature Distributions
- **Histograms:** Distribution of each predictor variable across African nations
- **Scatter Plots:** Relationship between top predictors (GDP, Schooling) and life expectancy

---

## Project Structure

```
linear_regression_model/
├── summative/
│   ├── linear_regression/
│   │   └── multivariate.ipynb          # Model development & comparison
│   ├── API/
│   │   ├── prediction.py               # FastAPI application
│   │   ├── best_model.joblib           # Trained model artifact
│   │   └── scaler.joblib               # StandardScaler for preprocessing
│   ├── flutterapp/                     # Mobile app for predictions
│   │   ├── lib/main.dart
│   │   └── pubspec.yaml
│   ├── pyproject.toml                  # Project configuration (uv)
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # This file
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- uv (Python package manager)
- Flutter SDK (for mobile app)

### Step 1: Install Dependencies
```bash
cd summative
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Step 2: Run the API Server Locally
```bash
cd API
uvicorn prediction:app --reload --port 8000
```

API will be available at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

### Step 3: Run the Flutter App
```bash
cd flutterapp
flutter pub get
flutter run
```

---

## API Endpoints

### 1. Health Check
```http
GET /
```
Returns API status and documentation link.

### 2. Make Prediction
```http
POST /predict
Content-Type: application/json

{
  "adult_mortality": 150.5,
  "infant_deaths": 25,
  "bmi": 22.5,
  "gdp": 5000.0,
  "schooling": 10.5
}
```

**Response:**
```json
{
  "predicted_life_expectancy_years": 68.42,
  "status": "success"
}
```

**Input Constraints (Pydantic Validation):**
- `adult_mortality`: 1.0 - 1000.0 (adult deaths per 1000 population)
- `infant_deaths`: 0 - 1000 (infant deaths per 1000 live births)
- `bmi`: 1.0 - 60.0 (body mass index)
- `gdp`: 10.0 - 150000.0 (USD per capita)
- `schooling`: 0.0 - 25.0 (years of education)

### 3. Trigger Model Retraining
```http
POST /retrain
```

Initiates background task to retrain model with updated data. Returns immediately with status.

---

## CORS Configuration

**Security Policy:** NOT using wildcard (*) - restricted to specific origins

**Allowed Origins:**
- `http://localhost` (local development)
- `http://localhost:8080` (development alternate port)
- `http://127.0.0.1` (localhost fallback)
- `https://*.onrender.com` (Render deployment)

**Allowed Methods:** GET, POST  
**Allowed Headers:** All  
**Credentials:** Enabled

**Rationale:**
- Restricts API access to known trusted domains only
- Prevents unauthorized cross-origin requests from random domains
- Enables local development and production deployment
- Allows credentials (cookies, auth headers) to be sent with requests

---

## Model Retraining Strategy

**Automatic Retraining Trigger:**
The API includes a `/retrain` endpoint that:
1. Loads the latest data file (`Life Expectancy Data.csv`)
2. Filters for African nations
3. Handles missing values via median imputation
4. Retrains the best-performing model
5. Updates the model and scaler artifacts (`best_model.joblib`, `scaler.joblib`)
6. Runs as a background task (non-blocking)

**When to Retrain:**
- New country data becomes available
- Significant global health events affect life expectancy trends
- Quarterly updates to WHO datasets
- Manual trigger via `/retrain` endpoint

---

## Deployment

### Hosting Platform: Render
1. Connect GitHub repository to Render
2. Configure build command: `pip install -r requirements.txt`
3. Configure start command: `uvicorn API.prediction:app --host 0.0.0.0 --port 8000`
4. Set environment variables as needed
5. Public URL structure: `https://your-app-name.onrender.com/docs`

---

## Video Demo

**Duration:** 7 minutes maximum  
**Contents:**
1. Flutter mobile app making predictions (2 min)
2. Swagger UI API testing with various inputs (2 min)
3. Model performance explanation using loss metrics (1.5 min)
4. Discussion of findings & hyperparameters (1.5 min)

---

## Key Questions Addressed in Video

### 1. **Is the Loss High or Low?**
- **MSE of 6.94 is relatively LOW** - The model explains 89.24% of variance (R² = 0.892)
- Compared to baseline linear models (MSE 35.63), Random Forest performs significantly better
- **Strategies to reduce loss further:**
  - Feature engineering: Create interaction terms (e.g., GDP × Schooling)
  - Hyperparameter tuning: Optimize n_estimators, max_depth, min_samples_split
  - Collect more data: More African nations and years would improve generalization
  - Feature scaling: Ensure all features are on similar scales for better model learning
  - Domain knowledge: Include additional health indicators (life expectancy drivers)

### 2. **What are Hyperparameters?**
- **Definition:** Parameters set BEFORE training that control how the model learns
- **Examples for Random Forest:**
  - `n_estimators=100`: Number of decision trees in the forest
  - `max_depth`: Maximum depth of each tree (prevents overfitting)
  - `min_samples_split`: Minimum samples required to split a node
  - `min_samples_leaf`: Minimum samples in leaf nodes
  - `random_state=42`: Ensures reproducible results
- **Impact:** Better hyperparameters → Better model performance, faster training, reduced overfitting

### 3. **Updating Model with New Data in Deployment**
- **Trigger retraining:** Call `/retrain` endpoint when new data becomes available
- **Workflow:**
  1. New health data uploaded to server
  2. Flask background task initiates retraining
  3. Data preprocessed (scaling, missing value handling)
  4. New Random Forest model trained on updated dataset
  5. Best model artifacts saved (`best_model.joblib`, `scaler.joblib`)
  6. No API downtime - predictions use latest model automatically
- **Versioning:** Keep historical model versions for rollback if performance degrades

### 4. **CORS Middleware Configuration Rationale**
- **Why restrict origins instead of using wildcard (*):**
  - **Security:** Prevents unauthorized cross-origin requests from random domains
  - **Privacy:** Limits data exposure to known trusted clients only
  - **Control:** Explicit whitelist allows precise access management
  - **Compliance:** Follows OWASP and best practice guidelines for web APIs

- **Allowed origins in this project:**
  - `http://localhost` & `http://127.0.0.1`: Local development
  - `http://localhost:8080`: Alternate dev port
  - `https://*.onrender.com`: Production deployment
  
- **When to use wildcard (*):**
  - Public APIs with no sensitive data
  - During early prototyping only
  - Not recommended for production APIs

---

## Technologies Used

- **Backend:** FastAPI, Uvicorn, Pydantic
- **ML/Data:** Scikit-learn, Pandas, NumPy, Joblib
- **Frontend:** Flutter, Dart
- **Deployment:** Render
- **Package Management:** uv (Python), pub (Dart)
- **Notebooks:** Jupyter

---

## License

MIT License - See LICENSE file for details

---

## Author

Tyler  
[Date: 2026-07-25]

---

## References

- WHO Life Expectancy Dataset: https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Scikit-learn: https://scikit-learn.org/
- Flutter Documentation: https://flutter.dev/

# linear_regression_model
