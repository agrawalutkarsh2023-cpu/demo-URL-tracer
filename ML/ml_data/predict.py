"""
predict.py
Prediction interface for the trained Random Forest model.

Public functions (called by backend ml_service.py):
    load_model_once()       -- lazy singleton model loader
    predict(request_data)   -- single-record prediction
    batch_predict(records)  -- list of predictions

Output format:
    {
        "prediction":   "SQL Injection",
        "confidence":   0.91,
        "label":        "Prototype Prediction",
        "model":        "RandomForest"
    }

If confidence < LOW_CONFIDENCE_THRESHOLD:
    {"prediction": "LOW_CONFIDENCE", "confidence": <score>, ...}

DEMO PROTOTYPE -- all predictions are on synthetic / demo data only.
"""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Make sure sibling modules importable when run directly
sys.path.insert(0, os.path.dirname(__file__))

from features import extract_features_from_record, FEATURE_NAMES
from model import load_model as _load_model_raw

# --- Confidence threshold --------------------------------------------------------
LOW_CONFIDENCE_THRESHOLD = 0.55  # below this -> return LOW_CONFIDENCE

# --- Singleton state -------------------------------------------------------------
_model   = None
_encoder = None
_model_available = False


def load_model_once() -> bool:
    """
    Lazy-load the trained model exactly once per process.

    Returns
    -------
    bool -- True if model loaded successfully, False otherwise.
    The backend can use this to decide whether to fall back to rule-based detection.
    """
    global _model, _encoder, _model_available
    if _model_available:
        return True
    try:
        _model, _encoder = _load_model_raw()
        _model_available = True
        logger.info("[predict] Random Forest model loaded successfully.")
        return True
    except FileNotFoundError:
        logger.warning(
            "[predict] ML model not found. "
            "Run 'python ml_data/train.py' to train it. "
            "Falling back to rule-based detection."
        )
        _model_available = False
        return False
    except Exception as e:
        logger.error(f"[predict] Failed to load model: {e}")
        _model_available = False
        return False


def predict(request_data: dict) -> dict:
    """
    Predict the attack type for a single HTTP request record.

    Parameters
    ----------
    request_data : dict
        Must contain at minimum 'url'.
        Optional: method, host, status_code, response_size, user_agent.

    Returns
    -------
    dict:
        {
            "prediction":   str,    # attack class or "LOW_CONFIDENCE" or "Benign"
            "confidence":   float,  # max class probability [0, 1]
            "label":        str,    # always "Prototype Prediction"
            "model":        str,    # "RandomForest" | "unavailable"
            "ml_available": bool
        }
    """
    if not load_model_once():
        return {
            "prediction":   "Benign",
            "confidence":   0.0,
            "label":        "Prototype Prediction",
            "model":        "unavailable",
            "ml_available": False,
        }

    try:
        features = extract_features_from_record(request_data)
        feature_vector = [features[f] for f in FEATURE_NAMES]

        probabilities = _model.predict_proba([feature_vector])[0]
        max_confidence = float(probabilities.max())
        predicted_index = int(probabilities.argmax())
        predicted_class = _encoder.inverse_transform([predicted_index])[0]

        if max_confidence < LOW_CONFIDENCE_THRESHOLD:
            return {
                "prediction":   "LOW_CONFIDENCE",
                "confidence":   round(max_confidence, 4),
                "label":        "Prototype Prediction",
                "model":        "RandomForest",
                "ml_available": True,
            }

        return {
            "prediction":   predicted_class,
            "confidence":   round(max_confidence, 4),
            "label":        "Prototype Prediction",
            "model":        "RandomForest",
            "ml_available": True,
        }

    except Exception as e:
        logger.error(f"[predict] Prediction error: {e}")
        return {
            "prediction":   "Benign",
            "confidence":   0.0,
            "label":        "Prototype Prediction",
            "model":        "error",
            "ml_available": False,
        }


def batch_predict(records: list[dict]) -> list[dict]:
    """
    Run predict() over a list of request records.

    Parameters
    ----------
    records : list[dict]

    Returns
    -------
    list[dict]  -- same length as input, same order
    """
    return [predict(r) for r in records]


def get_model_status() -> dict:
    """
    Return model availability status and metadata.
    Used by the /api/ml/status endpoint.
    """
    available = load_model_once()
    status = {
        "ml_available":    available,
        "model_type":      "RandomForest" if available else None,
        "confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
        "label":           "Prototype Prediction",
        "disclaimer":      "This is a demo prototype trained on synthetic data only. Not production-ready.",
    }
    if available and _model is not None:
        try:
            status["n_estimators"]  = int(_model.n_estimators)
            status["n_classes"]     = int(_model.n_classes_)
            status["classes"]       = list(_encoder.classes_)
            status["n_features"]    = int(_model.n_features_in_)
        except Exception:
            pass
    return status


# --- CLI demo --------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    demo_requests = [
        {
            "url": "/search?id=1' UNION SELECT username,password FROM users--",
            "method": "GET",
            "host": "demo-app.internal",
            "status_code": 200,
            "response_size": 1245,
        },
        {
            "url": "/search?q=<script>alert(document.cookie)</script>",
            "method": "GET",
            "host": "demo-app.internal",
            "status_code": 200,
            "response_size": 850,
        },
        {
            "url": "/download?file=../../etc/passwd",
            "method": "GET",
            "host": "demo-app.internal",
            "status_code": 200,
            "response_size": 2048,
        },
        {
            "url": "/api/items/42",
            "method": "GET",
            "host": "demo-app.internal",
            "status_code": 200,
            "response_size": 512,
        },
        {
            "url": "/ping?host=127.0.0.1;cat /etc/passwd",
            "method": "GET",
            "host": "demo-app.internal",
            "status_code": 200,
            "response_size": 300,
        },
    ]

    print("\n" + "=" * 60)
    print("  Prototype Prediction Demo")
    print("=" * 60)

    status = get_model_status()
    print(f"\nModel status: {'[OK] Available' if status['ml_available'] else '✗ Not trained'}")
    if not status["ml_available"]:
        print("  -> Run: python ml_data/train.py")
        sys.exit(1)

    print(f"Classes: {status.get('classes', [])}")
    print(f"Confidence threshold: {LOW_CONFIDENCE_THRESHOLD}\n")

    for req in demo_requests:
        result = predict(req)
        conf_bar = "#" * int(result["confidence"] * 30)
        print(f"  URL:        {req['url'][:60]}")
        print(f"  Prediction: {result['prediction']:<25}  Confidence: {result['confidence']:.2%}  {conf_bar}")
        print(f"  Label:      {result['label']}")
        print()
