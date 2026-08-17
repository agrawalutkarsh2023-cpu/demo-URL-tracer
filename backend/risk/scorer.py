"""
risk/scorer.py
IP Risk Score calculator for the DEMO system.

Points are configurable constants — easy to tune for the hackathon demo.
Scores are computed from synthetic detection results only.
"""

from typing import Optional

# ─────────────────────────────────────────────
# Point values per attack type (easy to change)
# ─────────────────────────────────────────────
ATTACK_POINTS: dict[str, int] = {
    "SQL Injection": 30,
    "Directory Traversal": 30,
    "Command Injection": 35,
    "XSS": 20,
    "Brute Force": 25,
    "SSRF": 35,
    "LFI/RFI": 30,
    "XXE": 30,
    "Web Shell": 40,
    "Typosquatting": 20,
    "HTTP Parameter Pollution": 10,
    "Credential Stuffing": 25,
}

# Bonus for a simulated potential-success event
POTENTIAL_SUCCESS_BONUS = 40

# Bonus for high request rate (applied externally if needed)
HIGH_REQUEST_RATE_BONUS = 15

# ─────────────────────────────────────────────
# Risk level thresholds
# ─────────────────────────────────────────────
def get_risk_level(score: int) -> str:
    if score <= 20:
        return "LOW"
    if score <= 50:
        return "MEDIUM"
    if score <= 100:
        return "HIGH"
    return "CRITICAL"


def calculate_risk_score(
    detections: list[dict],
    request_count: int = 0,
    high_rate_threshold: int = 100,
) -> dict:
    """
    Calculate a risk score for a single IP based on its detection history.

    Parameters
    ----------
    detections : list of detection result dicts
        Each dict must have at least 'attack_type' and 'result' keys.
    request_count : int
        Total number of requests from this IP.
    high_rate_threshold : int
        Requests above this count trigger the high-rate bonus.

    Returns
    -------
    dict with keys: risk_score, risk_level
    """
    score = 0

    # Deduplicate attack types to avoid inflating score for repeated same-type hits
    seen_types: set[str] = set()

    for det in detections:
        attack_type = det.get("attack_type", "")
        result = det.get("result", "ATTEMPT")

        # Add base points for each unique attack type seen
        if attack_type not in seen_types:
            points = ATTACK_POINTS.get(attack_type, 10)
            score += points
            seen_types.add(attack_type)

        # Bonus for simulated success
        if result == "POTENTIAL_SUCCESS":
            score += POTENTIAL_SUCCESS_BONUS

    # High request rate bonus
    if request_count > high_rate_threshold:
        score += HIGH_REQUEST_RATE_BONUS

    return {
        "risk_score": score,
        "risk_level": get_risk_level(score),
    }
