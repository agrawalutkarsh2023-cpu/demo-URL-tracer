"""
features.py
Feature extraction for URL-based attack detection.

Extracts 13 numeric/boolean features from a raw HTTP request record.
All features are computed from the URL, HTTP method, status code,
response size, and host -- no external APIs required.

DEMO PROTOTYPE -- designed for use with the synthetic dataset.
"""

import re
import logging
from typing import Union
from urllib.parse import urlparse, parse_qs, unquote

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# --- Suspicious keywords per attack class ----------------------------------------
# Used to count how many attack-pattern keywords appear in a URL.
_SUSPICIOUS_KEYWORDS = [
    # SQL
    "select", "union", "insert", "update", "delete", "drop", "alter",
    "sleep(", "benchmark(", "1=1", "or '", "xp_",
    # XSS
    "<script", "onerror=", "onload=", "javascript:", "alert(", "document.cookie",
    "eval(", "<iframe", "<svg",
    # Command
    "whoami", "ls ", "cat /", "; id", "$(", "| bash", "wget ", "curl ",
    "/bin/sh", "/bin/bash", "passthru", "shell_exec", "system(",
    # Path traversal / LFI
    "../", "%2e%2e", "etc/passwd", "boot.ini", "win.ini", "php://", "file://",
    # SSRF
    "169.254", "metadata.google", "localhost", "127.0.0.1",
    # XXE
    "<!entity", "<!doctype", "system '", 'system "',
    # Webshell
    "shell.php", "cmd=", "exec=", "passthru(", "/c99", "/r57",
    # Typosquatting markers
    "paypa1", "g00gle", "faceb00k", "arnazon", "mlcrosoft",
]

# Compiled once for speed
_SUSPICIOUS_RE = re.compile(
    "|".join(re.escape(kw) for kw in _SUSPICIOUS_KEYWORDS),
    re.IGNORECASE,
)

_PERCENT_RE = re.compile(r"%[0-9a-fA-F]{2}")
_SPECIAL_CHARS = set("<>'\";(){}[]|\\`!@#$^&*")

_METHOD_MAP = {
    "GET": 0, "POST": 1, "PUT": 2, "DELETE": 3,
    "PATCH": 4, "HEAD": 5, "OPTIONS": 6, "TRACE": 7,
}


# --- Per-record feature extraction -----------------------------------------------

def extract_features_from_record(record: dict) -> dict:
    """
    Extract a flat dict of numeric features from a single HTTP request record.

    Parameters
    ----------
    record : dict
        Keys: url, method, host, status_code, response_size, user_agent

    Returns
    -------
    dict  -- 13 numeric features
    """
    url = str(record.get("url") or "")
    method = str(record.get("method") or "GET").upper()
    host = str(record.get("host") or "")
    status_code = int(record.get("status_code") or 0)
    response_size = int(record.get("response_size") or 0)

    # Decode percent-encoding once for keyword matching
    url_decoded = unquote(url).lower()
    combined = url_decoded + " " + host.lower()

    # Parse URL structure
    parsed = urlparse(url)
    path = parsed.path or ""
    query = parsed.query or ""

    # -- Feature 1: url_length
    url_length = len(url)

    # -- Feature 2: param_count  (number of distinct query parameters)
    try:
        params = parse_qs(query, keep_blank_values=True)
        param_count = len(params)
    except Exception:
        param_count = query.count("&") + (1 if query else 0)

    # -- Feature 3: special_char_count
    special_char_count = sum(1 for c in url if c in _SPECIAL_CHARS)

    # -- Feature 4: encoding_count  (%xx sequences)
    encoding_count = len(_PERCENT_RE.findall(url))

    # -- Feature 5: path_depth  (non-empty path segments)
    path_depth = len([s for s in path.split("/") if s])

    # -- Feature 6: suspicious_keyword_count
    suspicious_keyword_count = len(_SUSPICIOUS_RE.findall(combined))

    # -- Feature 7: http_method_encoded
    http_method_encoded = _METHOD_MAP.get(method, 8)

    # -- Feature 8: status_code
    # Already an integer

    # -- Feature 9: response_size
    # Already an integer

    # -- Feature 10: has_dot_dot  (directory traversal indicator)
    has_dot_dot = int(
        ".." in url or "%2e%2e" in url.lower() or "..../" in url
    )

    # -- Feature 11: has_base64  (base64-looking blobs often encode payloads)
    has_base64 = int(bool(re.search(r"(?:[A-Za-z0-9+/]{20,}={0,2})", url)))

    # -- Feature 12: is_post  (POST requests are higher risk for injection)
    is_post = int(method == "POST")

    # -- Feature 13: query_length
    query_length = len(query)

    return {
        "url_length":               url_length,
        "param_count":              param_count,
        "special_char_count":       special_char_count,
        "encoding_count":           encoding_count,
        "path_depth":               path_depth,
        "suspicious_keyword_count": suspicious_keyword_count,
        "http_method_encoded":      http_method_encoded,
        "status_code":              status_code,
        "response_size":            response_size,
        "has_dot_dot":              has_dot_dot,
        "has_base64":               has_base64,
        "is_post":                  is_post,
        "query_length":             query_length,
    }


FEATURE_NAMES = list(extract_features_from_record({}).keys())


# --- DataFrame-level extraction ---------------------------------------------------

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run extract_features_from_record over every row of a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned HTTP-record DataFrame (output of preprocessing.clean_data).

    Returns
    -------
    pd.DataFrame  -- shape (n, 13), columns = FEATURE_NAMES
    """
    records = df.to_dict(orient="records")
    feature_rows = [extract_features_from_record(r) for r in records]
    X = pd.DataFrame(feature_rows, columns=FEATURE_NAMES)
    logger.info(f"[extract_features] Extracted {len(FEATURE_NAMES)} features for {len(X)} rows")
    return X
