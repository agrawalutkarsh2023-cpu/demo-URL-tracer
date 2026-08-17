"""
detection/webshell.py
Web Shell Upload / Access detector.
Flags requests that look like web shell execution or upload attempts.
"""

import re
from typing import Optional

_EXECUTION_PATTERNS = [
    r"\.(php|asp|aspx|jsp|jspx|cfm|cgi|pl|py)\?(cmd|exec|command|run|shell|c|e|execute)=",
    r"/(shell|webshell|cmd|backdoor|hack|r57|c99|b374k)\.(php|asp|aspx|jsp)",
    r"/upload.*\.(php|asp|aspx|jsp)",
    r"passthru\s*\(",
    r"system\s*\(",
    r"shell_exec\s*\(",
    r"proc_open\s*\(",
    r"popen\s*\(",
    r"exec\s*\(",
    r"base64_decode\s*\(",
    r"\beval\s*\(",
    r"FilesystemObject",
    r"wscript\.shell",
    r"createobject\s*\(\s*['\"]shell",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _EXECUTION_PATTERNS]

_SUCCESS_CODES = {200}


def detect(request: dict) -> Optional[dict]:
    target = " ".join(filter(None, [
        request.get("url", ""),
        request.get("user_agent", ""),
    ]))

    hits = [p for p in _COMPILED if p.search(target)]
    if not hits:
        return None

    confidence = min(0.75 + len(hits) * 0.06, 0.99)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code in _SUCCESS_CODES else "ATTEMPT"

    return {
        "attack_type": "Web Shell",
        "severity": "CRITICAL",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }
