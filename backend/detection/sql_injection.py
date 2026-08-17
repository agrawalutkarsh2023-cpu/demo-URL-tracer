"""
detection/sql_injection.py
Rule-based SQL Injection detector.
Detects patterns like UNION SELECT, OR 1=1, stacked queries, etc.
"""

import re
from typing import Optional

# Patterns indicative of SQL injection attempts
_PATTERNS = [
    r"(UNION\s+SELECT)",
    r"(OR\s+1\s*=\s*1)",
    r"(AND\s+1\s*=\s*1)",
    r"(OR\s+'[^']*'\s*=\s*'[^']*')",
    r"(--\s*$)",
    r"(;\s*DROP\s+TABLE)",
    r"(;\s*DELETE\s+FROM)",
    r"(;\s*INSERT\s+INTO)",
    r"(;\s*UPDATE\s+\w+\s+SET)",
    r"(xp_cmdshell)",
    r"(EXEC\s*\()",
    r"(CAST\s*\(\s*\w+\s+AS\s+)",
    r"(CONVERT\s*\(\s*\w+\s*,)",
    r"(BENCHMARK\s*\()",
    r"(SLEEP\s*\(\s*\d+\s*\))",
    r"(WAITFOR\s+DELAY)",
    r"(information_schema)",
    r"(sysobjects)",
    r"(0x[0-9a-fA-F]{4,})",           # hex encoding
    r"(%27|%22|%3B|%2D%2D)",          # URL-encoded quotes / dashes
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

# Status codes that suggest potential success in simulated data
_SUCCESS_CODES = {200, 201, 202}


def detect(request: dict) -> Optional[dict]:
    """
    Analyse a single HTTP request dict for SQL Injection indicators.
    Returns a DetectionResult-compatible dict or None.
    """
    target = " ".join(filter(None, [
        request.get("url", ""),
        request.get("user_agent", ""),
        str(request.get("host", "")),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.60 + len(hits) * 0.08, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "SQL Injection",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
