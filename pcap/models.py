"""
models.py — Data models for the PCAP processing pipeline.
==========================================================

Plain Python dataclasses. No database, no ORM, no framework.
The backend receives these as plain Python dicts via .to_dict().

Does NOT:
  - Connect to any database
  - Import any web framework
  - Classify attacks
  - Score risk
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class ProcessingStatus(str, Enum):
    COMPLETED = "COMPLETED"   # At least one packet processed successfully
    ERROR     = "ERROR"       # File-level failure (missing, corrupted, etc.)
    NO_HTTP   = "NO_HTTP"     # File parsed, but zero HTTP / TLS traffic found


# ---------------------------------------------------------------------------
# Per-request record
# ---------------------------------------------------------------------------

@dataclass
class PacketRecord:
    """
    A single normalized HTTP request extracted from a PCAP packet.

    Every field that cannot be determined from the PCAP is set to None.
    Values are NEVER invented or guessed.
    """
    timestamp:        Optional[str] = None   # ISO 8601 UTC string
    source_ip:        Optional[str] = None
    destination_ip:   Optional[str] = None
    source_port:      Optional[int] = None
    destination_port: Optional[int] = None
    protocol:         Optional[str] = None   # "IPv4" | "IPv6"
    method:           Optional[str] = None   # GET, POST, PUT, …
    host:             Optional[str] = None   # HTTP Host header
    url:              Optional[str] = None   # Constructed: http://{host}{uri}
    user_agent:       Optional[str] = None   # HTTP User-Agent header
    status_code:      Optional[int] = None   # HTTP response code (if captured)
    response_size:    Optional[int] = None   # Content-Length from response

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Top-level processing result
# ---------------------------------------------------------------------------

@dataclass
class ProcessingResult:
    """
    The complete result returned by process_pcap() to the backend.

    The backend uses this dict to:
      - Store metadata (packets_processed, http_requests, …)
      - Forward records to the detection engine
      - Report uninspectable (TLS) counts to the frontend
    """
    status:               str           = ProcessingStatus.COMPLETED
    filename:             str           = ""
    packets_processed:    int           = 0
    http_requests:        int           = 0   # Successfully extracted HTTP requests
    inspectable_requests: int           = 0   # Same as http_requests (alias)
    uninspectable:        int           = 0   # TLS/HTTPS packets — not decoded
    records:              List[dict]    = field(default_factory=list)
    error:                Optional[str] = None  # Set only when status == ERROR

    def to_dict(self) -> dict:
        return {
            "status":               self.status,
            "filename":             self.filename,
            "packets_processed":    self.packets_processed,
            "http_requests":        self.http_requests,
            "inspectable_requests": self.inspectable_requests,
            "uninspectable":        self.uninspectable,
            "records":              self.records,
            "error":                self.error,
        }


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class PCAPError(Exception):
    """Raised when a PCAP file cannot be validated or loaded."""
    pass
