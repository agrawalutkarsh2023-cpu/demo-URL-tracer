"""
normalizer.py — Extracted field normalization.
==============================================

Takes raw dicts produced by extractor.py and converts them into
the standard output schema that the backend detection engine expects.

Rules:
  - Every field in the schema is ALWAYS present in the output dict.
  - Fields that cannot be determined from the packet are set to None.
  - Values are NEVER invented, guessed, or inferred beyond what the packet contains.

Does NOT:
  - Classify attacks            →  backend's job
  - Score risk                  →  backend's job
  - Connect to any service      →  demo module only
  - Modify or filter URL content →  URIs are preserved verbatim
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

def build_url(host: Optional[str], uri: Optional[str]) -> Optional[str]:
    """
    Construct a human-readable URL from the HTTP Host header and URI.

    Rules:
      host + uri  →  "http://{host}{uri}"       (full URL)
      uri only    →  "{uri}"                     (relative URL)
      neither     →  None

    URI content is preserved verbatim — percent-encoded attack strings
    are NOT decoded or sanitized here. The backend detection engine
    receives the raw URI as captured.

    Args:
        host: Value of the HTTP Host header (e.g. "demo.target.local").
        uri:  Request-URI from the HTTP request line (e.g. "/search?id=1").

    Returns:
        Constructed URL string, or None if uri is absent.
    """
    if not uri:
        return None
    if host:
        return f"http://{host}{uri}"
    return uri


# ---------------------------------------------------------------------------
# Single-record normalization
# ---------------------------------------------------------------------------

def normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a raw extraction dict into the standard PacketRecord schema.

    The output dict always contains every key listed below.
    Missing values use None — the string "N/A" or empty string are not used.

    Args:
        raw: Dict from extractor.extract_packet() for a CLASS_HTTP_REQUEST packet.

    Returns:
        Normalized dict matching the backend's expected schema.
    """
    return {
        # Network metadata
        "timestamp":        raw.get("timestamp"),
        "source_ip":        raw.get("source_ip"),
        "destination_ip":   raw.get("destination_ip"),
        "source_port":      raw.get("source_port"),
        "destination_port": raw.get("destination_port"),
        "protocol":         raw.get("protocol"),

        # HTTP request fields
        "method":           raw.get("method"),
        "host":             raw.get("host"),
        "url":              build_url(raw.get("host"), raw.get("uri")),
        "user_agent":       raw.get("user_agent"),

        # HTTP response fields — null for request-only captures
        "status_code":      raw.get("status_code",   None),
        "response_size":    raw.get("response_size", None),
    }


# ---------------------------------------------------------------------------
# Batch normalization
# ---------------------------------------------------------------------------

def normalize_all(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a list of raw extraction dicts.

    Args:
        records: List of raw dicts from extractor.extract_packet().

    Returns:
        List of normalized dicts, one per input record.
    """
    return [normalize_record(r) for r in records]
