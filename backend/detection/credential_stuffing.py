"""
detection/credential_stuffing.py
Credential Stuffing detector.
Flags high-frequency POST requests to login endpoints
from the same IP but with varying User-Agents (bot rotation pattern).
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

# In-memory state for demo
_ip_ua_map: dict[str, dict] = defaultdict(lambda: {"agents": set(), "times": []})

_LOGIN_PATHS = {"/login", "/signin", "/auth", "/api/login", "/account/login"}
_WINDOW_SECONDS = 120
_UA_THRESHOLD = 3         # unique user-agents from one IP → suspicious
_REQ_THRESHOLD = 6        # minimum total requests in window


def detect(request: dict) -> Optional[dict]:
    url = request.get("url", "")
    method = (request.get("method") or "").upper()
    source_ip = request.get("source_ip", "")
    ua = request.get("user_agent", "") or ""

    path = url.split("?")[0].rstrip("/").lower()
    is_login = any(path.endswith(lp) for lp in _LOGIN_PATHS)

    if not is_login or method != "POST":
        return None

    now = datetime.utcnow()
    window_start = now - timedelta(seconds=_WINDOW_SECONDS)

    state = _ip_ua_map[source_ip]
    state["times"] = [t for t in state["times"] if t > window_start]
    state["times"].append(now)
    if ua:
        state["agents"].add(ua[:80])    # cap UA string

    req_count = len(state["times"])
    ua_count = len(state["agents"])

    if req_count < _REQ_THRESHOLD or ua_count < _UA_THRESHOLD:
        return None

    confidence = min(0.65 + ua_count * 0.05, 0.97)
    result = "ATTEMPT"

    return {
        "attack_type": "Credential Stuffing",
        "severity": "HIGH",
        "confidence": round(confidence, 2),
        "detection_method": "RULE",
        "result": result,
    }


def reset_state():
    _ip_ua_map.clear()
