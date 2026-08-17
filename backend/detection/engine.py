"""
detection/engine.py
Central detection orchestrator.
Runs all modular detectors against a single HTTP request record
and returns the highest-confidence result.

All detections are on SYNTHETIC / DEMO data only.
"""

from typing import Optional

from detection import sql_injection
from detection import xss
from detection import directory_traversal
from detection import command_injection
from detection import ssrf
from detection import lfi_rfi
from detection import brute_force
from detection import credential_stuffing
from detection import http_param_pollution
from detection import xxe
from detection import webshell
from detection import typosquatting

# Ordered list of all detector modules
_DETECTORS = [
    command_injection,      # CRITICAL — check first
    webshell,               # CRITICAL
    sql_injection,
    directory_traversal,
    lfi_rfi,
    xxe,
    ssrf,
    brute_force,
    credential_stuffing,
    xss,
    http_param_pollution,
    typosquatting,
]

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def run_detection(request: dict) -> Optional[dict]:
    """
    Run all detectors against a single request dict.

    Returns the single best (highest-severity, then highest-confidence)
    detection result, or None if no attack is detected.

    Result schema:
    {
        "attack_type": str,
        "severity": str,      # LOW | MEDIUM | HIGH | CRITICAL
        "confidence": float,
        "detection_method": str,  # RULE | ML | HYBRID
        "result": str,            # ATTEMPT | POTENTIAL_SUCCESS
    }
    """
    results = []

    for detector in _DETECTORS:
        try:
            result = detector.detect(request)
            if result:
                # Strip any internal debug keys (prefixed with _)
                clean = {k: v for k, v in result.items() if not k.startswith("_")}
                results.append(clean)
        except Exception:
            # Individual detector failure must never crash the whole engine
            pass

    if not results:
        return None

    # Pick the best result: highest severity → highest confidence
    best = max(
        results,
        key=lambda r: (_SEVERITY_RANK.get(r.get("severity", "LOW"), 1), r.get("confidence", 0)),
    )

    return best


def run_all_detections(request: dict) -> list[dict]:
    """
    Run all detectors and return EVERY match (not just the best).
    Useful for detailed analysis views.
    """
    results = []
    for detector in _DETECTORS:
        try:
            result = detector.detect(request)
            if result:
                clean = {k: v for k, v in result.items() if not k.startswith("_")}
                results.append(clean)
        except Exception:
            pass
    return results
