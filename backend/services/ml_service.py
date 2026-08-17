"""
services/ml_service.py
ML module interface — bridges the FastAPI backend to the Random Forest model.

Integration strategy (graceful degradation):
  1. On startup, try to load the trained RF model from ml_data/models/rf_model.pkl
  2. If model is available → use it for predictions (detection_method = "ML")
  3. If model is NOT available (not yet trained) → fall back to the
     keyword-heuristic stub so the backend still works during development.

The backend calling code (csv_service.py, upload.py) does NOT need to change —
it calls predict(record) and gets back { "prediction": ..., "confidence": ... }.

DEMO PROTOTYPE — all data is synthetic.
"""

import logging
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Add ml_data to path so we can import from it ────────────────────────────────
_ML_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ML", "ml_data")
_ML_DIR = os.path.normpath(_ML_DIR)

if os.path.isdir(_ML_DIR) and _ML_DIR not in sys.path:
    sys.path.insert(0, _ML_DIR)

# ─── Try to import the RF predictor ──────────────────────────────────────────────
_rf_predict       = None
_rf_batch_predict = None
_rf_status        = None
_rf_loaded        = False

try:
    from predict import predict as _rf_predict_fn
    from predict import batch_predict as _rf_batch_fn
    from predict import get_model_status as _rf_status_fn
    from predict import load_model_once

    _rf_loaded = load_model_once()
    if _rf_loaded:
        _rf_predict       = _rf_predict_fn
        _rf_batch_predict = _rf_batch_fn
        _rf_status        = _rf_status_fn
        logger.info("[ml_service] Random Forest model loaded — using RF predictions.")
    else:
        logger.warning(
            "[ml_service] RF model not trained yet. "
            "Using keyword-heuristic fallback. "
            "Run: python ML/ml_data/train.py"
        )
except ImportError as e:
    logger.warning(f"[ml_service] Could not import ml_data modules: {e}. Using heuristic fallback.")


# ─── Keyword-heuristic fallback ──────────────────────────────────────────────────
# Used when the RF model has not been trained yet.
# Simulates ML output so the rest of the backend always works.

_KEYWORD_MAP: list[tuple[str, list[str]]] = [
    ("SQL Injection",           ["union", "select", "drop", "insert", "update", "delete", "1=1", "or '", "sleep(", "benchmark("]),
    ("Command Injection",       ["whoami", "ls ", "cat /", "; id", "$(", "&& ", "| bash", "wget ", "curl "]),
    ("Directory Traversal",     ["../", "%2e%2e", "/etc/passwd", "boot.ini", "win.ini"]),
    ("XSS",                     ["<script", "onerror=", "javascript:", "alert(", "document.cookie"]),
    ("SSRF",                    ["169.254", "localhost", "127.0.0.1", "metadata.google"]),
    ("LFI/RFI",                 ["php://", "file://", "include=http", "page=http", "../.."]),
    ("XXE",                     ["<!doctype", "<!entity", "system '", 'system "']),
    ("Web Shell Upload",        [".php?cmd=", "shell_exec", "passthru(", "system(", "/shell.php"]),
    ("Brute Force",             ["/login", "/signin", "/auth", "wp-login"]),
    ("Typosquatting",           ["paypa1", "g00gle", "faceb00k", "rn.com", "paypai"]),
    ("HTTP Parameter Pollution", ["param=a&param=b", "id=1&id=2"]),
    ("Credential Stuffing",     ["/login", "password=", "username=", "email="]),
]


def _heuristic_predict(request_data: dict) -> dict:
    """Keyword-bag heuristic — used only when RF model is unavailable."""
    text = " ".join(filter(None, [
        (request_data.get("url") or "").lower(),
        (request_data.get("host") or "").lower(),
        (request_data.get("user_agent") or "").lower(),
    ]))

    scores: dict[str, float] = {}
    for attack_type, keywords in _KEYWORD_MAP:
        hit_count = sum(1 for kw in keywords if kw.lower() in text)
        if hit_count > 0:
            confidence = min(0.55 + hit_count * 0.07, 0.92)
            scores[attack_type] = round(confidence, 2)

    if not scores:
        return {
            "prediction":   "Benign",
            "confidence":   0.85,
            "label":        "Prototype Prediction",
            "model":        "heuristic-fallback",
            "ml_available": False,
        }

    best = max(scores, key=lambda k: scores[k])
    return {
        "prediction":   best,
        "confidence":   scores[best],
        "label":        "Prototype Prediction",
        "model":        "heuristic-fallback",
        "ml_available": False,
    }


# ─── Public interface (called by csv_service.py, upload.py) ──────────────────────

def predict(request_data: dict) -> dict:
    """
    Predict attack type from an HTTP request record.

    Parameters
    ----------
    request_data : dict
        Must contain at least 'url'. Optional: method, host,
        status_code, response_size, user_agent.

    Returns
    -------
    dict:
        {
            "prediction":   str,    # e.g. "SQL Injection" | "Benign" | "LOW_CONFIDENCE"
            "confidence":   float,  # [0, 1]
            "label":        str,    # "Prototype Prediction"
            "model":        str,    # "RandomForest" | "heuristic-fallback"
            "ml_available": bool
        }
    """
    if _rf_loaded and _rf_predict is not None:
        return _rf_predict(request_data)
    return _heuristic_predict(request_data)


def batch_predict(records: list[dict]) -> list[dict]:
    """
    Run predict() over a list of request records.

    Returns
    -------
    list[dict]  — same length and order as input
    """
    if _rf_loaded and _rf_batch_predict is not None:
        return _rf_batch_predict(records)
    return [_heuristic_predict(r) for r in records]


def get_ml_status() -> dict:
    """
    Return ML model availability status.
    Called by GET /api/ml/status.
    """
    if _rf_loaded and _rf_status is not None:
        return _rf_status()
    return {
        "ml_available":         False,
        "model_type":           None,
        "confidence_threshold": 0.55,
        "label":                "Prototype Prediction",
        "disclaimer":           (
            "RF model not trained. "
            "Run: python ML/ml_data/train.py  "
            "Using keyword-heuristic fallback."
        ),
    }
