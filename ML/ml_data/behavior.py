"""
behavior.py
Simple IP-level behavioral analysis.

Detects:
  - Brute Force:           many failed logins from one IP in a short window
  - Credential Stuffing:   many distinct usernames from one IP
  - High Request Rate:     unusually high request rate from one IP

Also provides get_ip_features() for backend IP intelligence enrichment.

DEMO PROTOTYPE -- all analysis is on synthetic data only.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# --- Thresholds ------------------------------------------------------------------
BRUTE_FORCE_FAILED_THRESHOLD = 5       # failed login attempts in window
BRUTE_FORCE_WINDOW_SECONDS   = 60      # time window for brute force check
CRED_STUFFING_USERNAME_THRESHOLD = 3   # distinct usernames from one IP
HIGH_RATE_THRESHOLD          = 20      # requests per minute

LOGIN_ENDPOINTS_RE = re.compile(
    r"/(login|signin|auth|wp-login|admin/login|api/auth)",
    re.IGNORECASE,
)
USERNAME_RE = re.compile(
    r"(?:username|user|email|login)=([^&\s]+)",
    re.IGNORECASE,
)


# --- Helpers ---------------------------------------------------------------------

def _parse_ts(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string; return None on failure."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except Exception:
        return None


def _get_ip_rows(df: pd.DataFrame, ip: str) -> pd.DataFrame:
    """Filter DataFrame to rows belonging to the given source IP."""
    if "source_ip" not in df.columns:
        return pd.DataFrame()
    return df[df["source_ip"] == ip].copy()


# --- Behavioral detectors --------------------------------------------------------

def _check_brute_force(ip_df: pd.DataFrame) -> dict | None:
    """
    Brute Force: ≥5 failed login attempts from the same IP within 60 seconds.
    """
    # Filter to login endpoints
    login_rows = ip_df[
        ip_df["url"].str.contains(LOGIN_ENDPOINTS_RE, na=False)
    ]
    # Failed = status 401 or 403
    failed = login_rows[login_rows["status_code"].isin([401, 403])]

    if len(failed) < BRUTE_FORCE_FAILED_THRESHOLD:
        return None

    # Parse timestamps and look for a burst within the window
    failed = failed.copy()
    failed["_ts"] = failed["timestamp"].apply(_parse_ts)
    failed = failed.dropna(subset=["_ts"]).sort_values("_ts")

    # Sliding window check
    ts_list = list(failed["_ts"])
    for i in range(len(ts_list)):
        window_end = ts_list[i] + timedelta(seconds=BRUTE_FORCE_WINDOW_SECONDS)
        count_in_window = sum(1 for t in ts_list[i:] if t <= window_end)
        if count_in_window >= BRUTE_FORCE_FAILED_THRESHOLD:
            return {
                "behavior": "Brute Force",
                "severity": "HIGH",
                "evidence": (
                    f"{count_in_window} failed login attempts within "
                    f"{BRUTE_FORCE_WINDOW_SECONDS}s window"
                ),
                "failed_logins": int(len(failed)),
            }
    return None


def _check_credential_stuffing(ip_df: pd.DataFrame) -> dict | None:
    """
    Credential Stuffing: ≥3 distinct usernames tried from one IP.
    """
    login_rows = ip_df[
        ip_df["url"].str.contains(LOGIN_ENDPOINTS_RE, na=False)
    ]
    if login_rows.empty:
        return None

    usernames = set()
    for url in login_rows["url"].dropna():
        m = USERNAME_RE.search(str(url))
        if m:
            usernames.add(m.group(1).lower())

    if len(usernames) >= CRED_STUFFING_USERNAME_THRESHOLD:
        return {
            "behavior": "Credential Stuffing",
            "severity": "HIGH",
            "evidence": f"{len(usernames)} distinct usernames tried from this IP",
            "distinct_usernames": int(len(usernames)),
        }
    return None


def _check_high_request_rate(ip_df: pd.DataFrame) -> dict | None:
    """
    High Request Rate: ≥20 requests per minute from one IP.
    """
    ip_df = ip_df.copy()
    ip_df["_ts"] = ip_df["timestamp"].apply(_parse_ts)
    ip_df = ip_df.dropna(subset=["_ts"]).sort_values("_ts")

    if len(ip_df) < HIGH_RATE_THRESHOLD:
        return None

    ts_list = list(ip_df["_ts"])
    for i in range(len(ts_list)):
        window_end = ts_list[i] + timedelta(seconds=60)
        count = sum(1 for t in ts_list[i:] if t <= window_end)
        if count >= HIGH_RATE_THRESHOLD:
            return {
                "behavior": "High Request Rate",
                "severity": "MEDIUM",
                "evidence": f"{count} requests within 60s window",
                "requests_per_minute": int(count),
            }
    return None


# --- Public API -------------------------------------------------------------------

def analyze_behavior(df: pd.DataFrame, ip: str) -> list[dict]:
    """
    Run all behavioral checks for a given IP address.

    Parameters
    ----------
    df  : pd.DataFrame -- the full (cleaned) traffic DataFrame
    ip  : str          -- source IP to analyze

    Returns
    -------
    list of behavioral alert dicts (empty list = no alerts)
    Each dict has: behavior, severity, evidence, + detector-specific fields.
    """
    ip_df = _get_ip_rows(df, ip)
    if ip_df.empty:
        return []

    alerts = []
    for checker in [_check_brute_force, _check_credential_stuffing, _check_high_request_rate]:
        result = checker(ip_df)
        if result:
            result["source_ip"] = ip
            alerts.append(result)

    if alerts:
        logger.info(f"[analyze_behavior] {ip}: {[a['behavior'] for a in alerts]}")
    return alerts


def get_ip_features(df: pd.DataFrame, ip: str) -> dict:
    """
    Generate IP intelligence features for a given source IP.
    These are passed to the backend's IP analysis pipeline.

    Parameters
    ----------
    df : pd.DataFrame -- full cleaned traffic DataFrame
    ip : str

    Returns
    -------
    dict with:
        ip_address, total_requests, attack_count, attack_types,
        request_frequency_per_min, first_seen, last_seen,
        behavioral_alerts
    """
    ip_df = _get_ip_rows(df, ip)

    if ip_df.empty:
        return {
            "ip_address": ip,
            "total_requests": 0,
            "attack_count": 0,
            "attack_types": [],
            "request_frequency_per_min": 0.0,
            "first_seen": None,
            "last_seen": None,
            "behavioral_alerts": [],
        }

    total_requests = len(ip_df)

    # Attack count (rows where attack_type != Normal)
    if "attack_type" in ip_df.columns:
        attack_rows = ip_df[~ip_df["attack_type"].isin(["Normal", "Unknown", ""])]
        attack_count = len(attack_rows)
        attack_types = sorted(attack_rows["attack_type"].dropna().unique().tolist())
    else:
        attack_count = 0
        attack_types = []

    # Timestamps
    ip_df["_ts"] = ip_df["timestamp"].apply(_parse_ts)
    valid_ts = ip_df["_ts"].dropna()
    if not valid_ts.empty:
        first_seen = valid_ts.min().isoformat()
        last_seen  = valid_ts.max().isoformat()
        duration_secs = max((valid_ts.max() - valid_ts.min()).total_seconds(), 1)
        req_freq = round(total_requests / (duration_secs / 60), 2)
    else:
        first_seen = None
        last_seen  = None
        req_freq   = 0.0

    behavioral_alerts = analyze_behavior(df, ip)

    return {
        "ip_address":               ip,
        "total_requests":           int(total_requests),
        "attack_count":             int(attack_count),
        "attack_types":             attack_types,
        "request_frequency_per_min": float(req_freq),
        "first_seen":               first_seen,
        "last_seen":                last_seen,
        "behavioral_alerts":        behavioral_alerts,
    }


def get_all_ip_features(df: pd.DataFrame) -> list[dict]:
    """
    Run get_ip_features for every unique source IP in the dataset.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    list of IP feature dicts
    """
    if "source_ip" not in df.columns:
        return []
    unique_ips = df["source_ip"].dropna().unique().tolist()
    return [get_ip_features(df, ip) for ip in unique_ips]
