"""
detection/xxe.py
XML External Entity (XXE) Injection detector.
Looks for DOCTYPE / ENTITY declarations in URL or query parameters.
"""

import re
from typing import Optional

_PATTERNS = [
    r"<!DOCTYPE\b",
    r"<!ENTITY\b",
    r"SYSTEM\s+['\"]",
    r"PUBLIC\s+['\"]",
    r"%xxe",
    r"&xxe;",
    r"file:///",
    r"expect://",
    r"php://expect",
    r"%26%23x25%3B",               # double URL-encoded %
    r"<!%5BDOCTYPE",               # URL-encoded <!
    r"%3C%21DOCTYPE",
    r"%3C%21ENTITY",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

_SUCCESS_CODES = {200}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [
        request.get("url", ""),
        request.get("user_agent", ""),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.70 + len(hits) * 0.06, 0.98)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "XXE",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
