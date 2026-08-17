"""
detection/typosquatting.py
Typosquatting / URL Spoofing detector.
Uses Levenshtein distance to compare request host against known-legitimate domains.
"""

from typing import Optional

try:
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    # Fallback pure-Python implementation
    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
            prev = curr
        return prev[-1]


# Simulated "known legitimate" domains for the demo
_KNOWN_DOMAINS = [
    "google.com", "gmail.com", "youtube.com",
    "facebook.com", "instagram.com", "twitter.com",
    "amazon.com", "paypal.com", "apple.com",
    "microsoft.com", "linkedin.com", "netflix.com",
    "github.com", "stackoverflow.com", "reddit.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com",
    "irs.gov", "sbi.co.in", "icicibank.com", "hdfcbank.com",
]

# Maximum Levenshtein distance to flag as suspicious
_MAX_DISTANCE = 3
# Minimum domain length to consider (avoid flagging very short names)
_MIN_LEN = 6


def detect(request: dict) -> Optional[dict]:
    host = (request.get("host") or "").lower().strip()
    if not host or len(host) < _MIN_LEN:
        return None

    # Strip port if present
    host = host.split(":")[0]

    # Skip if the host exactly matches a known domain
    if host in _KNOWN_DOMAINS:
        return None

    best_distance = None
    best_match = None

    for domain in _KNOWN_DOMAINS:
        # Only compare if lengths are reasonably similar
        if abs(len(host) - len(domain)) > _MAX_DISTANCE + 1:
            continue
        d = levenshtein_distance(host, domain)
        if best_distance is None or d < best_distance:
            best_distance = d
            best_match = domain

    if best_distance is None or best_distance > _MAX_DISTANCE or best_distance == 0:
        return None

    # Confidence inversely proportional to distance
    confidence = round(max(0.50, 0.90 - best_distance * 0.12), 2)

    return {
        "attack_type": "Typosquatting",
        "severity": "MEDIUM",
        "confidence": confidence,
        "detection_method": "RULE",
        "result": "ATTEMPT",
        "_matched_against": best_match,   # extra debug info (stripped by engine)
    }
