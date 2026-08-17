"""
api/ml.py
ML-specific REST endpoints.

GET  /api/ml/status       — Is the RF model loaded? Which classes? 
POST /api/ml/predict      — Run a single-record RF prediction
POST /api/ml/predict/batch — Batch prediction
GET  /api/ml/metrics      — Return the last recorded evaluation metrics

DEMO PROTOTYPE — synthetic data only.
All outputs carry the "Prototype Prediction" label.
"""

import json
import os
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.ml_service import predict as ml_predict, batch_predict as ml_batch, get_ml_status

logger = logging.getLogger(__name__)
router = APIRouter()

# Path to stored metrics (written by train.py via the metrics endpoint)
_METRICS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "ML", "ml_data", "models", "metrics.json"
)
_METRICS_FILE = os.path.normpath(_METRICS_FILE)


# ─── Schemas ─────────────────────────────────────────────────────────────────────

class MLRequest(BaseModel):
    url: str = Field(..., example="/search?id=1' OR '1'='1")
    method: Optional[str] = Field("GET", example="GET")
    host: Optional[str] = Field(None, example="demo-app.internal")
    user_agent: Optional[str] = Field(None, example="Mozilla/5.0")
    status_code: Optional[int] = Field(None, example=200)
    response_size: Optional[int] = Field(None, example=1024)


class MLResponse(BaseModel):
    prediction: str
    confidence: float
    label: str
    model: str
    ml_available: bool


class BatchMLRequest(BaseModel):
    records: list[MLRequest] = Field(..., min_length=1, max_length=500)


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@router.get("/ml/status", tags=["ML"])
def ml_status():
    """
    Returns the current ML model availability status.
    Frontend uses this to show the ML panel state.
    """
    return get_ml_status()


@router.post("/ml/predict", response_model=MLResponse, tags=["ML"])
def ml_predict_single(req: MLRequest):
    """
    Run a single HTTP request through the Random Forest classifier.

    Returns the predicted attack type and confidence score.
    If confidence < threshold, returns prediction = "LOW_CONFIDENCE".

    Note: This is a PROTOTYPE PREDICTION on synthetic/demo data only.
    """
    result = ml_predict(req.model_dump())
    return MLResponse(**result)


@router.post("/ml/predict/batch", tags=["ML"])
def ml_predict_batch(req: BatchMLRequest):
    """
    Run batch predictions over multiple HTTP request records.
    Returns a list of prediction dicts in the same order as the input.
    """
    records = [r.model_dump() for r in req.records]
    results = ml_batch(records)
    return {
        "count":   len(results),
        "results": results,
        "label":   "Prototype Prediction",
    }


@router.get("/ml/metrics", tags=["ML"])
def ml_metrics():
    """
    Return the evaluation metrics from the last training run.

    Metrics are actual measured values from the held-out test set.
    They are saved to ml_data/models/metrics.json by train.py.

    If the model has not been trained yet, returns a 404.
    """
    if not os.path.exists(_METRICS_FILE):
        raise HTTPException(
            status_code=404,
            detail=(
                "No metrics found. Train the model first: "
                "python ML/ml_data/train.py"
            ),
        )
    try:
        with open(_METRICS_FILE, "r") as f:
            metrics = json.load(f)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read metrics: {e}")
