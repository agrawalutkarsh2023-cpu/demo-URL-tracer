"""
services/ml_service.py
ML module interface for the DEMO prototype.

This stub provides a clean predict() interface. A real scikit-learn or
TensorFlow model can be dropped in here without changing any calling code.

Current implementation: keyword-frequency heuristic that simulates ML output
with realistic confidence scores for the demo.
"""

import re
from typing import Optional

# Keyword bags per attack class — simulates what a TF-IDF model would learn
_KEYWORD_MAP: list[tuple[str, list[str]]] = [
    ("SQL Injection",           ["union", "select", "drop", "insert", "update", "delete", "1=1", "or '", "sleep(", "benchmark("]),
    ("Command Injection",       ["whoami", "ls ", "cat /", "; id", "$(", "&&", "| bash", "wget ", "curl "]),
    ("Directory Traversal",     ["../", "%2e%2e", "/etc/passwd", "boot.ini", "win.ini"]),
    ("XSS",                     ["<script", "onerror=", "javascript:", "alert(", "document.cookie"]),
    ("SSRF",                    ["169.254", "localhost", "127.0.0.1", "metadata.google"]),
    ("LFI/RFI",                 ["php://", "file://", "include=http", "page=http", "../.."]),
    ("XXE",                     ["<!doctype", "<!entity", "system '", "system \""]),
    ("Web Shell",               [".php?cmd=", "shell_exec", "passthru(", "system(", "/shell.php"]),
    ("Brute Force",             ["/login", "/signin", "/auth", "wp-login"]),
    ("Typosquatting",           ["paypa1", "g00gle", "faceb00k", "rn.com", "paypai"]),
    ("HTTP Parameter Pollution",["param=a&param=b", "id=1&id=2"]),
    ("Credential Stuffing",     ["/login", "password=", "username=", "email="]),
]


def predict(request_data: dict) -> dict:
    """
    Predict attack type from an HTTP request record.

    Parameters
    ----------
    request_data : dict
        Must contain at least 'url'. Optional: host, user_agent.

    Returns
    -------
    dict: { "prediction": str, "confidence": float }
    """
    text = " ".join(filter(None, [
        (request_data.get("url") or "").lower(),
        (request_data.get("host") or "").lower(),
        (request_data.get("user_agent") or "").lower(),
    ]))

    scores: dict[str, float] = {}

    for attack_type, keywords in _KEYWORD_MAP:
        hit_count = sum(1 for kw in keywords if kw.lower() in text)
        if hit_count > 0:
            # Simulate confidence: more keyword hits → higher confidence
            base = 0.55
            confidence = min(base + hit_count * 0.08, 0.97)
            scores[attack_type] = round(confidence, 2)

    if not scores:
        return {"prediction": "Benign", "confidence": 0.85}

    best_attack = max(scores, key=lambda k: scores[k])
    return {
        "prediction": best_attack,
        "confidence": scores[best_attack],
    }


def batch_predict(requests: list[dict]) -> list[dict]:
    """
    Run predict() over a list of request records.
    Returns a list of prediction dicts in the same order.
    """
    return [predict(r) for r in requests]
