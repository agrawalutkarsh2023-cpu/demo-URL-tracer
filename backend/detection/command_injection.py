"""
detection/command_injection.py
Rule-based OS Command Injection detector.
"""

import re
from typing import Optional

_PATTERNS = [
    r";\s*ls\b",
    r";\s*cat\s+/",
    r";\s*id\b",
    r";\s*whoami\b",
    r";\s*uname\b",
    r";\s*wget\s+",
    r";\s*curl\s+",
    r";\s*nc\s+",
    r";\s*netcat\s+",
    r"&&\s*(ls|cat|id|whoami|uname|wget|curl)",
    r"\|\s*(ls|cat|id|whoami|uname|wget|curl)",
    r"\|\|\s*(ls|cat|id|whoami|uname)",
    r"\$\([^)]+\)",                   # $(command)
    r"`[^`]+`",                       # `command`
    r"%60[^%]+%60",                   # URL-encoded backtick
    r";\s*rm\s+-rf",
    r";\s*chmod\s+",
    r";\s*python\s+-c",
    r";\s*perl\s+-e",
    r";\s*php\s+-r",
    r"%3B",                           # URL-encoded ;
    r"%26%26",                        # URL-encoded &&
    r"%7C",                           # URL-encoded |
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

_SUCCESS_CODES = {200}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [
        request.get("url", ""),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.70 + len(hits) * 0.06, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "Command Injection",
        "severity": "CRITICAL",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
