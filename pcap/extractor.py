"""
extractor.py — Packet-level data extraction.
=============================================

Responsibilities:
  - Extract IP/TCP metadata (IPs, ports, timestamp) from each Scapy packet
  - Detect TLS/HTTPS traffic and mark it as UNINSPECTABLE
  - Parse raw TCP payloads for HTTP/1.x request lines and headers
  - Return a (data_dict, classification) pair for each packet

Does NOT:
  - Classify attacks (SQL injection, XSS, etc.)  →  backend's job
  - Attempt to decrypt HTTPS                      →  impossible without keys
  - Write to database                             →  backend's job
  - Call any external service                     →  demo module only

Classification labels
---------------------
  CLASS_HTTP_REQUEST  — Inspectable HTTP request; data_dict has all HTTP fields
  CLASS_ENCRYPTED     — TLS/HTTPS; counted as uninspectable, URL never fabricated
  CLASS_NON_HTTP      — All other TCP or non-TCP traffic; skipped silently
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from scapy.all import IP, IPv6, Raw, TCP

# ---------------------------------------------------------------------------
# Classification labels
# ---------------------------------------------------------------------------

CLASS_HTTP_REQUEST = "http_request"
CLASS_ENCRYPTED    = "encrypted"
CLASS_NON_HTTP     = "non_http"

# ---------------------------------------------------------------------------
# HTTP detection
# ---------------------------------------------------------------------------

# All HTTP request method prefixes (space after each — part of the spec)
_HTTP_METHODS: tuple = (
    b"GET ",
    b"POST ",
    b"PUT ",
    b"DELETE ",
    b"PATCH ",
    b"HEAD ",
    b"OPTIONS ",
    b"CONNECT ",
    b"TRACE ",
)

# ---------------------------------------------------------------------------
# TLS detection constants
# ---------------------------------------------------------------------------

# TLS Record Content-Type values (RFC 5246 / RFC 8446)
_TLS_CONTENT_TYPES: frozenset = frozenset({
    0x14,  # ChangeCipherSpec
    0x15,  # Alert
    0x16,  # Handshake
    0x17,  # ApplicationData
})

# Major version byte shared by SSLv3 / TLS 1.0-1.3 (all use 0x03 as major)
_TLS_VERSION_MAJOR: int = 0x03

# Well-known HTTPS ports
_HTTPS_PORTS: frozenset = frozenset({443, 8443})


# ---------------------------------------------------------------------------
# Timestamp helper
# ---------------------------------------------------------------------------

def _get_timestamp(pkt) -> str:
    """
    Return the packet's capture timestamp as an ISO 8601 UTC string.
    Falls back to the current wall-clock time if the field is missing.
    """
    try:
        dt = datetime.fromtimestamp(float(pkt.time), tz=timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# IP / TCP metadata
# ---------------------------------------------------------------------------

def _get_ip_metadata(pkt) -> Dict[str, Optional[str]]:
    """Extract source IP, destination IP, and IP protocol version."""
    if IP in pkt:
        return {
            "source_ip":      pkt[IP].src,
            "destination_ip": pkt[IP].dst,
            "protocol":       "IPv4",
        }
    if IPv6 in pkt:
        return {
            "source_ip":      pkt[IPv6].src,
            "destination_ip": pkt[IPv6].dst,
            "protocol":       "IPv6",
        }
    return {"source_ip": None, "destination_ip": None, "protocol": None}


def _get_tcp_metadata(pkt) -> Dict[str, Optional[int]]:
    """Extract TCP source and destination ports."""
    if TCP in pkt:
        return {
            "source_port":      pkt[TCP].sport,
            "destination_port": pkt[TCP].dport,
        }
    return {"source_port": None, "destination_port": None}


# ---------------------------------------------------------------------------
# TLS / HTTPS detection
# ---------------------------------------------------------------------------

def is_tls(pkt) -> bool:
    """
    Return True if the packet appears to be TLS/HTTPS traffic.

    IMPORTANT: This function only DETECTS encrypted traffic.
    It does NOT decrypt or inspect encrypted content.

    Detection heuristics (any single match is sufficient):
      1. Destination or source port is a known HTTPS port (443, 8443).
      2. Raw TCP payload starts with a TLS Content-Type byte (0x14–0x17)
         immediately followed by the TLS major version byte (0x03).

    These heuristics cover TLS 1.0 / 1.1 / 1.2 / 1.3 and SSLv3.
    """
    if TCP not in pkt:
        return False

    # Heuristic 1: well-known HTTPS port
    if pkt[TCP].sport in _HTTPS_PORTS or pkt[TCP].dport in _HTTPS_PORTS:
        return True

    # Heuristic 2: TLS record header signature in raw payload
    if Raw in pkt:
        payload: bytes = bytes(pkt[Raw])
        if (
            len(payload) >= 3
            and payload[0] in _TLS_CONTENT_TYPES
            and payload[1] == _TLS_VERSION_MAJOR
        ):
            return True

    return False


# ---------------------------------------------------------------------------
# HTTP/1.x request parser
# ---------------------------------------------------------------------------

def parse_http_request(raw_payload: bytes) -> Optional[Dict[str, Any]]:
    """
    Attempt to parse a raw TCP payload as an HTTP/1.x request.

    Extracts:
      method      — HTTP verb (GET, POST, …)
      uri         — Request-URI (path + query string)
      host        — HTTP Host header value
      user_agent  — HTTP User-Agent header value
      content_type— HTTP Content-Type header value (or None)

    Args:
        raw_payload: Raw bytes from the TCP payload.

    Returns:
        A dict of extracted fields, or None if this is not an HTTP request.
    """
    # Fast rejection: check for a known HTTP method prefix
    if not any(raw_payload.startswith(m) for m in _HTTP_METHODS):
        return None

    try:
        # Decode permissively (replace unknown bytes rather than raising)
        text: str = raw_payload.decode("utf-8", errors="replace")
        lines = text.split("\r\n")

        if not lines:
            return None

        # --- Request line: "METHOD URI HTTP/version" ---
        request_line_parts = lines[0].split(" ")
        if len(request_line_parts) < 2:
            return None

        method: str = request_line_parts[0].strip().upper()
        uri: str    = request_line_parts[1].strip() if len(request_line_parts) > 1 else "/"

        # --- Header parsing ---
        headers: Dict[str, str] = {}
        for line in lines[1:]:
            if line == "":
                break  # Blank line signals end of headers
            if ": " in line:
                key, _, value = line.partition(": ")
                headers[key.lower().strip()] = value.strip()

        return {
            "method":       method,
            "uri":          uri,
            "host":         headers.get("host")         or None,
            "user_agent":   headers.get("user-agent")   or None,
            "content_type": headers.get("content-type") or None,
        }

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main per-packet extraction function
# ---------------------------------------------------------------------------

def extract_packet(pkt) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Classify and extract data from a single Scapy packet.

    Pipeline:
      1. Build base metadata (timestamp, IPs, ports)
      2. Skip non-TCP packets → CLASS_NON_HTTP
      3. Check for TLS/HTTPS  → CLASS_ENCRYPTED  (no URL fabrication)
      4. Require raw payload  → CLASS_NON_HTTP if absent
      5. Parse HTTP request   → CLASS_HTTP_REQUEST on success
      6. Otherwise            → CLASS_NON_HTTP

    Args:
        pkt: A single Scapy packet object.

    Returns:
        (data_dict, classification)

        data_dict:      dict of extracted fields, or None for CLASS_NON_HTTP
        classification: one of CLASS_HTTP_REQUEST | CLASS_ENCRYPTED | CLASS_NON_HTTP

    CRITICAL:
        For CLASS_ENCRYPTED packets, data_dict will contain base IP/TCP
        metadata but NO url, host, or method — those fields are never
        fabricated from encrypted traffic.
    """
    # --- Base metadata (always extracted) ---
    ip_meta  = _get_ip_metadata(pkt)
    tcp_meta = _get_tcp_metadata(pkt)
    base: Dict[str, Any] = {
        "timestamp": _get_timestamp(pkt),
        **ip_meta,
        **tcp_meta,
    }

    # --- Only TCP can carry HTTP or TLS ---
    if TCP not in pkt:
        return None, CLASS_NON_HTTP

    # --- TLS / HTTPS detection ---
    # IMPORTANT: encrypted traffic is classified here and returned immediately.
    # The URL, host, and method fields are intentionally absent — never invented.
    if is_tls(pkt):
        return {**base, "encrypted": True}, CLASS_ENCRYPTED

    # --- HTTP requires a raw payload ---
    if Raw not in pkt:
        return None, CLASS_NON_HTTP

    raw_payload: bytes = bytes(pkt[Raw])

    # --- HTTP/1.x request parsing ---
    http_data = parse_http_request(raw_payload)
    if http_data:
        return {**base, **http_data}, CLASS_HTTP_REQUEST

    # Everything else (ACK-only, binary protocols, HTTP responses, …)
    return None, CLASS_NON_HTTP
