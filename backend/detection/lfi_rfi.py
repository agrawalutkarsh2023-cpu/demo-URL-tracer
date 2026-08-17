"""
detection/lfi_rfi.py
Rule-based Local File Inclusion / Remote File Inclusion (LFI/RFI) detector.
"""

import re
from typing import Optional

_PATTERNS = [
    r"php://input",
    r"php://filter",
    r"php://fd",
    r"data://",
    r"phar://",
    r"zip://",
    r"glob://",
    r"expect://",
    r"file=https?://",              # RFI via URL param
    r"include=https?://",
    r"page=https?://",
    r"path=https?://",
    r"\.\./.*\.(php|asp|jsp|txt|ini|log|conf|bak)",
    r"/proc/self/fd/",
    r"/var/log/(apache|nginx|auth|syslog)",
    r"c:\\\\inetpub",
    r"(include|require)(_once)?\s*\(",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

_SUCCESS_CODES = {200}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [request.get("url", "")]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.68 + len(hits) * 0.07, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "LFI/RFI",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
