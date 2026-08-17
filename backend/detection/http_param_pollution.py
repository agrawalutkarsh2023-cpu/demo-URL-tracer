"""
detection/http_param_pollution.py
HTTP Parameter Pollution (HPP) detector.
Flags URLs with duplicate query-string parameter names.
"""

from urllib.parse import urlparse, parse_qs
from typing import Optional


def detect(request: dict) -> Optional[dict]:
    url = request.get("url", "") or ""

    # Parse query string
    try:
        parsed = urlparse(url)
        qs = parsed.query
    except Exception:
        return None

    if not qs:
        return None

    params = parse_qs(qs, keep_blank_values=True)
    # parse_qs already groups duplicates — any param with >1 value is polluted
    duplicated = {k: v for k, v in params.items() if len(v) > 1}

    if not duplicated:
        return None

    dup_count = len(duplicated)
    confidence = min(0.55 + dup_count * 0.10, 0.90)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code == 200 else "ATTEMPT"

    return {
        "attack_type": "HTTP Parameter Pollution",
        "severity": "MEDIUM",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
