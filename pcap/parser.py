"""
parser.py — PCAP file validation and loading.
=============================================

Responsibilities:
  - Validate the file exists, is readable, has correct extension (.pcap / .pcapng)
  - Confirm the file is not empty
  - Load the PCAP using Scapy and return a PacketList

Does NOT:
  - Parse individual packets  →  extractor.py
  - Classify traffic          →  backend's responsibility
  - Write to database         →  backend's responsibility
  - Create any network socket →  demo module only
"""

import os
from pathlib import Path

from scapy.all import rdpcap, Scapy_Exception

from .models import PCAPError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS: set = {".pcap", ".pcapng"}

# Safety limit — prevents accidentally loading huge files in demo context
MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def validate_pcap(file_path: str) -> Path:
    """
    Validate that a PCAP file is safe to load.

    Checks (in order):
      1. File exists on disk
      2. File is readable by the current process
      3. Extension is .pcap or .pcapng
      4. File is not empty (0 bytes)
      5. File size is within the demo limit (100 MB)

    Args:
        file_path: Absolute or relative path to the PCAP file.

    Returns:
        A pathlib.Path object for the validated file.

    Raises:
        PCAPError: Descriptive message for any validation failure.
    """
    path = Path(file_path)

    # --- Existence ---
    if not path.exists():
        raise PCAPError(f"File not found: {file_path}")

    # --- Readability ---
    if not os.access(path, os.R_OK):
        raise PCAPError(f"File is not readable (check permissions): {file_path}")

    # --- Extension ---
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise PCAPError(
            f"Unsupported file extension '{suffix}'. "
            f"Accepted extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # --- Non-empty ---
    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise PCAPError(f"File is empty (0 bytes): {file_path}")

    # --- Size limit ---
    if size_bytes > MAX_FILE_SIZE_BYTES:
        size_mb = size_bytes / (1024 * 1024)
        raise PCAPError(
            f"File is too large ({size_mb:.1f} MB). "
            f"Demo limit is {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    return path


def load_pcap(file_path: str):
    """
    Load a PCAP file and return a Scapy PacketList.

    Assumes validate_pcap() has already been called.

    Args:
        file_path: Path to the validated PCAP file.

    Returns:
        scapy.plist.PacketList — the full list of packets.

    Raises:
        PCAPError: If Scapy cannot parse the file (corrupted, truncated, etc.)
                   or if the file contains zero packets.
    """
    try:
        packets = rdpcap(str(file_path))
    except Scapy_Exception as exc:
        raise PCAPError(
            f"Scapy could not parse the PCAP file (possibly corrupted or "
            f"unsupported capture format): {exc}"
        ) from exc
    except Exception as exc:
        raise PCAPError(f"Unexpected error reading PCAP file: {exc}") from exc

    if len(packets) == 0:
        raise PCAPError("PCAP file parsed successfully but contains zero packets.")

    return packets
