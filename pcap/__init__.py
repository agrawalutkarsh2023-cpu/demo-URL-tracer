"""
pcap — PCAP Processing Module
==============================

Extracts HTTP request records from .pcap / .pcapng files.

Backend integration (the ONLY interface needed):

    from pcap.processor import process_pcap

    result = process_pcap("demo/demo_attacks.pcap")

See README.md for the full output schema and integration guide.
"""

from .processor import process_pcap

__all__ = ["process_pcap"]
