"""
detection/directory_traversal.py
Rule-based Path / Directory Traversal detector.
"""

import re
from typing import Optional

_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e%2f",           # URL-encoded ../
    r"%2e%2e/",
    r"\.\.%2f",
    r"%252e%252e",          # double URL-encoded
    r"/etc/passwd",
    r"/etc/shadow",
    r"c:\\windows\\system32",
    r"boot\.ini",
    r"win\.ini",
    r"/proc/self/environ",
    r"\.\.%5c",             # URL-encoded ..\
    r"(\.\./){2,}",         # multiple traversal steps
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

_SUCCESS_CODES = {200}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [
        request.get("url", ""),
        request.get("host", ""),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.65 + len(hits) * 0.07, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "Directory Traversal",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
