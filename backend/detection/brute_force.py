"""
detection/brute_force.py
Stateful Brute Force detector.
Tracks per-IP login attempt counts within a rolling time window.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

# In-memory state for the demo (resets on server restart — acceptable for prototype)
_ip_login_attempts: dict[str, list[datetime]] = defaultdict(list)

# Configuration
_LOGIN_PATHS = {"/login", "/signin", "/auth", "/wp-login.php", "/admin/login", "/api/login"}
_WINDOW_SECONDS = 60          # 1-minute window
_THRESHOLD_ATTEMPTS = 8       # flag after this many requests


def detect(request: dict) -> Optional[dict]:
    url = request.get("url", "")
    method = (request.get("method") or "").upper()
    source_ip = request.get("source_ip", "")

    # Only flag POST-like requests to login endpoints
    path = url.split("?")[0].rstrip("/").lower()
    is_login_path = any(path.endswith(lp) for lp in _LOGIN_PATHS)

    if not is_login_path or method not in {"POST", "GET"}:
        return None

    now = datetime.utcnow()
    window_start = now - timedelta(seconds=_WINDOW_SECONDS)

    # Prune old attempts outside the window
    _ip_login_attempts[source_ip] = [
        t for t in _ip_login_attempts[source_ip] if t > window_start
    ]
    _ip_login_attempts[source_ip].append(now)

    count = len(_ip_login_attempts[source_ip])
    if count < _THRESHOLD_ATTEMPTS:
        return None

    confidence = min(0.60 + (count - _THRESHOLD_ATTEMPTS) * 0.04, 0.97)
    status_code = request.get("status_code")
    result = "POTENTIAL_SUCCESS" if status_code == 200 else "ATTEMPT"

    return {
        "attack_type": "Brute Force",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }


def reset_state():
    """Clear in-memory state — useful for testing."""
    _ip_login_attempts.clear()
