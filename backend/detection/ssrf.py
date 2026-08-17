"""
detection/ssrf.py
Rule-based Server-Side Request Forgery (SSRF) detector.
"""

import re
from typing import Optional

# Internal / metadata endpoints that should never be reached from a URL param
_INTERNAL_PATTERNS = [
    r"(https?://)?localhost",
    r"(https?://)?127\.0\.0\.1",
    r"(https?://)?0\.0\.0\.0",
    r"169\.254\.169\.254",             # AWS/GCP metadata
    r"metadata\.google\.internal",
    r"(https?://)?10\.\d+\.\d+\.\d+",
    r"(https?://)?172\.(1[6-9]|2\d|3[01])\.\d+\.\d+",
    r"(https?://)?192\.168\.\d+\.\d+",
    r"file://",
    r"dict://",
    r"gopher://",
    r"ftp://[^/]*@",
    r"%40localhost",                   # URL-encoded @ + localhost bypass
    r"0x7f000001",                     # Hex 127.0.0.1
    r"2130706433",                     # Decimal 127.0.0.1
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INTERNAL_PATTERNS]

_SUCCESS_CODES = {200, 201}


def detect(request: dict) -> Optional[dict]:
    # Look in URL parameters (the most common SSRF vector)
    url = request.get("url", "")
    if "=" not in url:
        return None

    # Only examine query-string values
    qs = url.split("?", 1)[1] if "?" in url else url

    hits = [p for p in _COMPILED if p.search(qs)]
    if not hits:
        return None

    confidence = min(0.72 + len(hits) * 0.07, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "SSRF",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
