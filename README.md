### Network Security Project for Phishing Data 
An end-to-end **MLOps pipeline** that detects phishing URLs using machine learning. Raw network data flows from **MongoDB Atlas** through automated ingestion, validation, transformation, and model training — then gets served via a **FastAPI** REST API for real-time predictions.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Seed the Database](#seed-the-database)
- [Running the Application](#running-the-application)
  - [Local (Python)](#local-python)
  - [Docker](#docker)
- [API Endpoints](#api-endpoints)
- [ML Pipeline](#ml-pipeline)
- [Experiment Tracking](#experiment-tracking)
- [Project Configuration](#project-configuration)
- [Contributing](#contributing)

---

## Overview

**Net-secudml** is a production-style machine learning project built for binary classification of phishing vs. legitimate network activity. It follows a modular MLOps design with clearly separated components for data ingestion, validation, transformation, model training, and serving.

Key capabilities:
- Pulls raw phishing data directly from **MongoDB Atlas**
- Validates dataset schema and detects statistical drift (KS-test)
- Preprocesses features using **KNN Imputation + Robust Scaling**
- Trains and evaluates a classification model with automated quality gates
- Tracks all experiments via **MLflow + DagsHub**
- Exposes `/train` and `/predict` endpoints via **FastAPI**
- Fully containerised with **Docker** and automated via **GitHub Actions**

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Net_Data/phisingData.csv  ──►  push_data.py         │
│                                 (one-time seed)       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
              MongoDB Atlas (Atulai.NetData)
                         │
          ┌──────────────▼──────────────┐
          │      TrainingPipeline       │
          │  ┌──────────────────────┐   │
          │  │   Data Ingestion     │   │  → train.csv / test.csv
          │  └──────────┬───────────┘   │
          │  ┌──────────▼───────────┐   │
          │  │   Data Validation    │   │  → schema check + drift report
          │  └──────────┬───────────┘   │
          │  ┌──────────▼───────────┐   │
          │  │  Data Transformation │   │  → KNNImputer + RobustScaler
          │  └──────────┬───────────┘   │
          │  ┌──────────▼───────────┐   │
          │  │    Model Trainer     │   │  → model.pkl + MLflow logging
          │  └──────────────────────┘   │
          └─────────────────────────────┘
                         │
              final_model/model.pkl
              final_model/preprocessor.pkl
                         │
          ┌──────────────▼──────────────┐
          │       FastAPI (app.py)       │
          │  GET  /train  → retrain      │
          │  POST /predict → CSV upload  │
          └─────────────────────────────┘
```

---

## Project Structure

```
Net-secudml/
├── .github/workflows/
│   └── main.yaml                  # CI/CD: build → push Docker image → deploy
│
├── Net_Data/
│   └── phisingData.csv            # Raw phishing dataset (source)
│
├── data_schema/
│   └── schema.yaml                # Column names and types for validation
│
├── final_model/
│   ├── model.pkl                  # Trained classifier (production artifact)
│   └── preprocessor.pkl           # Fitted sklearn preprocessing pipeline
│
├── netsecurity/                   # Core Python package
│   ├── components/
│   │   ├── data_ingestion.py      # MongoDB → train/test CSV
│   │   ├── data_validation.py     # Schema + KS-drift validation
│   │   ├── data_transformation.py # KNNImputer, RobustScaler, numpy arrays
│   │   └── model_trainer.py       # Train, evaluate, MLflow log, save
│   │
│   ├── constants/
│   │   └── training_pipeline.py   # All constants (paths, DB names, thresholds)
│   │
│   ├── entity/
│   │   ├── config_entity.py       # Typed config dataclasses per pipeline stage
│   │   └── artifact_entity.py     # Typed artifact dataclasses (stage outputs)
│   │
│   ├── exception/
│   │   └── exception.py           # Custom exception with file + line context
│   │
│   ├── logging/
│   │   └── logger.py              # Timestamped log files under Logs/
│   │
│   ├── pipeline/
│   │   └── training_pipeline.py   # Orchestrates all four components
│   │
│   └── utils/
│       ├── main_utils/utils.py    # save_object / load_object (pickle helpers)
│       └── ml_utils/
│           ├── metric/classification_metric.py  # F1, precision, recall
│           └── model/estimator.py               # NetworkModel (preprocess + predict)
│
├── app.py                         # FastAPI serving layer
├── main.py                        # Manual pipeline runner (dev/debug)
├── push_data.py                   # One-time: CSV → MongoDB Atlas
├── test_mongodb.py                # MongoDB connectivity smoke test
├── Dockerfile
├── requirements.txt
├── setup.py
└── README.md
```

---

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10 |
| ML / Data | scikit-learn, pandas, numpy |
| Database | MongoDB Atlas (pymongo) |
| Experiment Tracking | MLflow, DagsHub |
| API Framework | FastAPI, Uvicorn |
| Containerisation | Docker |
| CI/CD | GitHub Actions |
| Config | python-dotenv, pyaml |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional, for containerised run)
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account and cluster
- A [DagsHub](https://dagshub.com) account (for MLflow experiment tracking)

### Installation

```bash
# Clone the repository
git clone https://github.com/atull31/Net-secudml.git
cd Net-secudml

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Install the netsecurity package in editable mode
pip install -e .
```

### Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URL_KEY=mongodb+srv://<username>:<password>@cluster0.b4ajam9.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_URL=mongodb+srv://<username>:<password>@cluster0.b4ajam9.mongodb.net/?retryWrites=true&w=majority
```

> **Note:** Both variables point to the same MongoDB Atlas cluster. `MONGODB_URL_KEY` is used by `app.py` and the pipeline; `MONGO_DB_URL` is used by `push_data.py`.

### Seed the Database

This is a one-time step to upload the raw CSV dataset into MongoDB Atlas:

```bash
python push_data.py
```

This reads `Net_Data/phisingData.csv`, converts it to JSON records, and inserts them into the `Atulai` database under the `NetData` collection.

To verify your MongoDB connection independently:

```bash
python test_mongodb.py
```

---

## Running the Application

### Local (Python)

**Option 1 — Run the full pipeline manually (dev/debug):**

```bash
python main.py
```

This runs all four pipeline stages in sequence (Ingestion → Validation → Transformation → Training) and prints each artifact to stdout.

**Option 2 — Start the API server:**

```bash
python app.py
```

The server starts on `http://0.0.0.0:8000`. Visit `http://localhost:8000` to be redirected to the interactive Swagger docs at `/docs`.

### Docker

```bash
# Build the image
docker build -t net-secudml .

# Run the container
docker run -p 8000:8000 \
  -e MONGODB_URL_KEY="mongodb+srv://..." \
  net-secudml
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Redirects to `/docs` (Swagger UI) |
| `GET` | `/train` | Triggers the full training pipeline |
| `POST` | `/predict` | Upload a CSV file and get phishing predictions |

### `GET /train`

Triggers a full pipeline run: data ingestion → validation → transformation → model training. Returns `"Training is successful"` on completion.

> ⚠️ This is a synchronous, blocking call. The server will be unresponsive to other requests while training runs.

### `POST /predict`

Upload a CSV file with the same feature columns as the training data. Returns an HTML table with the original data plus a `predicted_column` field.

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: text/html" \
  -F "file=@your_data.csv"
```

**Prediction values:**
- `0` — Legitimate
- `1` — Phishing

---

## ML Pipeline

The training pipeline runs four sequential stages, each producing a typed artifact consumed by the next:

### 1. Data Ingestion (`data_ingestion.py`)
- Queries all records from `Atulai.NetData` in MongoDB
- Drops the `_id` field, replaces `"na"` strings with `NaN`
- Performs an 80/20 train-test split
- Writes `train.csv` and `test.csv` to `Artifacts/{timestamp}/data_ingestion/ingested/`

### 2. Data Validation (`data_validation.py`)
- Reads expected column names and count from `data_schema/schema.yaml`
- Validates both train and test splits against the schema
- Runs a **Kolmogorov-Smirnov test** on each feature column to detect distribution drift between train and test
- Writes a `drift_report.yaml` and copies valid files to `validated/`

### 3. Data Transformation (`data_transformation.py`)
- Separates features (`X`) from target (`Result`); remaps labels: `-1 → 0`, `1 → 1`
- Builds a sklearn `Pipeline`:
  - `KNNImputer(n_neighbors=3)` — fills missing values using nearest neighbours
  - `RobustScaler()` — scales using median/IQR (robust to outliers)
- Fits the pipeline on training data, transforms both splits
- Saves arrays as `.npy` files; saves the fitted preprocessor as `preprocessor.pkl`

### 4. Model Training (`model_trainer.py`)
- Loads the numpy arrays, separates features and labels
- Trains and selects the best classifier via cross-validation
- Evaluates on both train and test sets (F1, precision, recall)
- Enforces quality gates: minimum F1 score of **0.6** and overfitting check
- Logs metrics and the model to **MLflow / DagsHub**
- Saves the final model to `final_model/model.pkl`

---

## Experiment Tracking

This project uses **MLflow** backed by **DagsHub** for remote experiment tracking.

Metrics logged per run:
- `f1_score`
- `precision`
- `recall`

The `model_trainer.py` calls:
```python
import dagshub
dagshub.init(repo_owner="atull31", repo_name="Net-secudml", mlflow=True)
```

To view experiments locally:
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Then open `http://localhost:5000` in your browser.

---

## Project Configuration

All pipeline constants are centralised in `netsecurity/constants/training_pipeline.py`. Key values:

| Constant | Default | Purpose |
|---|---|---|
| `DATA_INGESTION_DATABASE_NAME` | `"Atulai"` | MongoDB database name |
| `DATA_INGESTION_COLLECTION_NAME` | `"NetData"` | MongoDB collection name |
| `DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO` | `0.2` | Train/test split ratio |
| `TARGET_COLUMN` | `"Result"` | Name of the label column |
| `MODEL_TRAINER_EXPECTED_SCORE` | `0.6` | Minimum acceptable F1 score |
| `SCHEMA_FILE_PATH` | `"data_schema/schema.yaml"` | Path to the schema definition |

Each pipeline stage creates its artifacts under a **timestamped directory**:
```
Artifacts/
└── {MM_DD_YYYY_HH_MM_SS}/
    ├── data_ingestion/
    ├── data_validation/
    ├── data_transformation/
    └── model_trainer/
```

This ensures no run overwrites a previous one's artifacts.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

*Built by [Atul Kumar](https://github.com/atull31)*
