"""
detection/xss.py
Rule-based Cross-Site Scripting (XSS) detector.
"""

import re
from typing import Optional

_PATTERNS = [
    r"<script[\s>]",
    r"</script>",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
    r"onmouseover\s*=",
    r"alert\s*\(",
    r"prompt\s*\(",
    r"confirm\s*\(",
    r"document\.cookie",
    r"document\.write",
    r"window\.location",
    r"eval\s*\(",
    r"<img[^>]+src\s*=\s*['\"]?\s*x",
    r"<svg[^>]+onload",
    r"<iframe",
    r"%3Cscript",                      # URL-encoded <script
    r"&#\d+;",                         # HTML entity encoding
    r"\\u003c",                        # Unicode escape
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

_SUCCESS_CODES = {200, 201}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [
        request.get("url", ""),
        request.get("user_agent", ""),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.55 + len(hits) * 0.09, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "XSS",
        "severity": "MEDIUM",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
