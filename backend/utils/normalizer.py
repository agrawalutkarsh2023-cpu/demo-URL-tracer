"""
utils/normalizer.py
Normalizes varied CSV/PCAP column names into the canonical HTTPRequest schema.

The canonical field names are:
  timestamp, source_ip, destination_ip, method, host,
  url, user_agent, status_code, response_size
"""

from datetime import datetime
from typing import Optional

# Maps possible CSV column names → canonical field name
_COLUMN_MAP: dict[str, str] = {
    # timestamp
    "timestamp": "timestamp",
    "time": "timestamp",
    "datetime": "timestamp",
    "date_time": "timestamp",
    "ts": "timestamp",
    "@timestamp": "timestamp",
    # source_ip
    "source_ip": "source_ip",
    "src_ip": "source_ip",
    "srcip": "source_ip",
    "src": "source_ip",
    "client_ip": "source_ip",
    "clientip": "source_ip",
    "ip": "source_ip",
    "remote_addr": "source_ip",
    # destination_ip
    "destination_ip": "destination_ip",
    "dst_ip": "destination_ip",
    "dstip": "destination_ip",
    "dest_ip": "destination_ip",
    "server_ip": "destination_ip",
    # method
    "method": "method",
    "http_method": "method",
    "request_method": "method",
    "verb": "method",
    # host
    "host": "host",
    "hostname": "host",
    "http_host": "host",
    "domain": "host",
    "server_name": "host",
    # url
    "url": "url",
    "uri": "url",
    "path": "url",
    "request_uri": "url",
    "request_url": "url",
    "request": "url",
    # user_agent
    "user_agent": "user_agent",
    "useragent": "user_agent",
    "ua": "user_agent",
    "http_user_agent": "user_agent",
    "agent": "user_agent",
    # status_code
    "status_code": "status_code",
    "status": "status_code",
    "http_status": "status_code",
    "response_code": "status_code",
    "code": "status_code",
    # response_size
    "response_size": "response_size",
    "bytes": "response_size",
    "size": "response_size",
    "content_length": "response_size",
    "body_bytes_sent": "response_size",
    "resp_size": "response_size",
}

_REQUIRED_FIELD = "source_ip"

_CANONICAL_FIELDS = {
    "timestamp", "source_ip", "destination_ip", "method",
    "host", "url", "user_agent", "status_code", "response_size",
}


def normalize_columns(raw_columns: list[str]) -> dict[str, str]:
    """
    Returns a mapping { raw_col: canonical_col } for recognized columns.
    Unrecognized columns are ignored.
    """
    mapping = {}
    for col in raw_columns:
        cleaned = col.strip().lower()
        if cleaned in _COLUMN_MAP:
            canonical = _COLUMN_MAP[cleaned]
            # First match wins (avoid overwriting)
            if canonical not in mapping.values():
                mapping[col] = canonical
    return mapping


def normalize_row(raw: dict, column_mapping: dict[str, str]) -> Optional[dict]:
    """
    Apply column_mapping to a raw CSV row and return a canonical record.
    Returns None if the required source_ip field is missing/empty.
    """
    record: dict = {}
    for raw_col, canonical in column_mapping.items():
        value = raw.get(raw_col)
        if value is not None and str(value).strip():
            record[canonical] = str(value).strip()

    if not record.get(_REQUIRED_FIELD):
        return None

    # Type coercions
    if "status_code" in record:
        try:
            record["status_code"] = int(record["status_code"])
        except (ValueError, TypeError):
            record.pop("status_code", None)

    if "response_size" in record:
        try:
            record["response_size"] = int(record["response_size"])
        except (ValueError, TypeError):
            record.pop("response_size", None)

    return record


def parse_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
    """Try common timestamp formats and return a datetime or None."""
    if not ts_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%d/%b/%Y:%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str.split("+")[0].strip(), fmt)
        except ValueError:
            continue
    return None
