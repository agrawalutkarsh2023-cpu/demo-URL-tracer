"""
processor.py — Main PCAP processing pipeline.
=============================================

This is the ONLY file the backend needs to import.

Backend integration:

    from pcap.processor import process_pcap

    result = process_pcap("demo/demo_attacks.pcap")

process_pcap() never raises exceptions — all errors are captured and
returned as a structured dict with status="ERROR".

Pipeline:
    PCAP file path
        ↓  validate_pcap()        — existence, extension, size
        ↓  load_pcap()            — Scapy rdpcap()
        ↓  extract_packet()       — per-packet: IP/TCP + HTTP/TLS detection
        ↓  normalize_record()     — standard schema
        ↓  ProcessingResult dict  — returned to backend

Does NOT:
  - Classify attacks (SQL injection, XSS, …)  →  backend's responsibility
  - Score risk                                →  backend's responsibility
  - Import ML model                           →  ml_model module's responsibility
  - Write to database                         →  backend's responsibility
  - Create API endpoints                      →  backend's responsibility
  - Capture live traffic                      →  demo prototype only
"""

import os
from typing import Any, Dict

from .extractor import CLASS_ENCRYPTED, CLASS_HTTP_REQUEST, extract_packet
from .models import PCAPError, ProcessingResult, ProcessingStatus
from .normalizer import normalize_record
from .parser import load_pcap, validate_pcap


def process_pcap(file_path: str) -> Dict[str, Any]:
    """
    Process a .pcap or .pcapng file and return structured HTTP records.

    This is the single entry point for the backend.

    Args:
        file_path: Absolute or relative path to a .pcap or .pcapng file.

    Returns:
        A dict with the following keys:

        Key                   Type            Description
        ---                   ----            -----------
        status                str             "COMPLETED" | "ERROR" | "NO_HTTP"
        filename              str             Basename of the input file
        packets_processed     int             Total packets iterated
        http_requests         int             HTTP requests successfully extracted
        inspectable_requests  int             Same as http_requests (alias)
        uninspectable         int             TLS/HTTPS packets — not decoded
        records               list[dict]      Normalized PacketRecord dicts
        error                 str | None      Error message (only when status=ERROR)

    Each record in `records` has the schema:
        {
            "timestamp":        str | None,
            "source_ip":        str | None,
            "destination_ip":   str | None,
            "source_port":      int | None,
            "destination_port": int | None,
            "protocol":         str | None,
            "method":           str | None,
            "host":             str | None,
            "url":              str | None,
            "user_agent":       str | None,
            "status_code":      int | None,
            "response_size":    int | None,
        }

    Example:
        >>> from pcap.processor import process_pcap
        >>> result = process_pcap("demo/demo_attacks.pcap")
        >>> print(result["status"])          # "COMPLETED"
        >>> print(result["http_requests"])   # e.g. 11
        >>> print(result["uninspectable"])   # e.g. 2
        >>> for rec in result["records"]:
        ...     print(rec["url"])
    """
    filename = os.path.basename(file_path)
    result = ProcessingResult(filename=filename)

    # ------------------------------------------------------------------
    # Step 1: Validate the file
    # ------------------------------------------------------------------
    try:
        validate_pcap(file_path)
    except PCAPError as exc:
        result.status = ProcessingStatus.ERROR
        result.error  = str(exc)
        return result.to_dict()

    # ------------------------------------------------------------------
    # Step 2: Load packets with Scapy
    # ------------------------------------------------------------------
    try:
        packets = load_pcap(file_path)
    except PCAPError as exc:
        result.status = ProcessingStatus.ERROR
        result.error  = str(exc)
        return result.to_dict()

    # ------------------------------------------------------------------
    # Step 3: Iterate and classify each packet
    # ------------------------------------------------------------------
    raw_http_records = []

    for pkt in packets:
        result.packets_processed += 1

        try:
            data, classification = extract_packet(pkt)
        except Exception:
            # Safely skip any packet that triggers an unexpected error.
            # Never let a single malformed packet crash the pipeline.
            continue

        if classification == CLASS_HTTP_REQUEST and data is not None:
            raw_http_records.append(data)
            result.http_requests        += 1
            result.inspectable_requests += 1

        elif classification == CLASS_ENCRYPTED:
            # Encrypted packet is COUNTED but its content is not decoded.
            # No URL is fabricated. No record is added.
            result.uninspectable += 1

        # CLASS_NON_HTTP: included in packets_processed, otherwise ignored.

    # ------------------------------------------------------------------
    # Step 4: Normalize all HTTP records into the standard schema
    # ------------------------------------------------------------------
    result.records = [normalize_record(r) for r in raw_http_records]

    # ------------------------------------------------------------------
    # Step 5: Assign final status
    # ------------------------------------------------------------------
    if result.http_requests == 0 and result.uninspectable == 0:
        result.status = ProcessingStatus.NO_HTTP
    else:
        result.status = ProcessingStatus.COMPLETED

    return result.to_dict()
