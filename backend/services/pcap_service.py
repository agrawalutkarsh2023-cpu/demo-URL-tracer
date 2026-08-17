"""
services/pcap_service.py
PCAP module interface for the DEMO prototype.

Public interface: process_pcap(file_path: str) -> list[dict]

The stub generates synthetic normalized HTTP records from the PCAP file's
byte count (to give variable but deterministic output), so the demo works
without a real PCAP parser or scapy dependency.

A real implementation (using scapy / pyshark) can replace the body of
process_pcap() without changing any calling code in the API layer.
"""

import os
import random
import hashlib
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# Synthetic data pools (fictional IPs & URLs)
# ─────────────────────────────────────────────
_ATTACK_URLS = [
    "/search?q=' OR 1=1--",
    "/api/user?id=1 UNION SELECT password FROM users--",
    "/login?user=admin'--",
    "/<script>alert('xss')</script>",
    "/img?src=<img onerror=alert(1)>",
    "/files/../../../etc/passwd",
    "/download?file=../../../../boot.ini",
    "/cmd?exec=;whoami",
    "/run?cmd=$(cat /etc/shadow)",
    "/api/fetch?url=http://169.254.169.254/latest/meta-data",
    "/include?page=php://filter/convert.base64-encode/resource=index.php",
    "/xml?data=<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
    "/uploads/shell.php?cmd=id",
    "/login",
    "/signin",
    "/wp-login.php",
    "/search?q=test&q=malicious",
    "/api/data",
    "/index.php",
    "/dashboard",
]

_BENIGN_URLS = [
    "/index.html",
    "/about",
    "/contact",
    "/products",
    "/api/health",
    "/favicon.ico",
    "/static/app.js",
    "/api/user/profile",
]

_SOURCE_IPS = [
    "10.0.0.5", "10.0.0.12", "10.0.0.23", "10.0.0.47",
    "192.168.1.10", "192.168.1.25", "192.168.2.5",
    "172.16.0.8", "172.16.1.15",
]

_METHODS = ["GET", "POST", "PUT", "DELETE"]
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "sqlmap/1.7.2#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "curl/7.88.1",
    "python-requests/2.31.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1)",
    "Wget/1.21.3",
]


def process_pcap(file_path: str) -> list[dict]:
    """
    Interface: parse a PCAP file and return normalized HTTP records.

    Current implementation: STUB — generates synthetic records seeded by
    the PCAP file's size, giving different but stable output per file.

    Replace this function body with real scapy/pyshark logic when available.

    Parameters
    ----------
    file_path : str
        Absolute path to the uploaded PCAP file.

    Returns
    -------
    list[dict]
        Each dict conforms to the canonical HTTPRequest schema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PCAP file not found: {file_path}")

    # Seed RNG from file size for deterministic but varied output
    file_size = os.path.getsize(file_path)
    rng = random.Random(file_size)

    # Simulate extracting between 30–120 HTTP records from the PCAP
    num_records = rng.randint(30, 120)
    records = []
    base_time = datetime.utcnow() - timedelta(minutes=num_records)

    for i in range(num_records):
        is_attack = rng.random() < 0.40     # ~40% attack traffic in sim
        url = rng.choice(_ATTACK_URLS if is_attack else _BENIGN_URLS)
        status = rng.choice([200, 200, 301, 400, 403, 404, 500]) if not is_attack else rng.choice([200, 403, 404, 500])

        record = {
            "timestamp": (base_time + timedelta(seconds=i * 3)).isoformat(),
            "source_ip": rng.choice(_SOURCE_IPS),
            "destination_ip": "192.168.100.1",
            "method": rng.choice(_METHODS),
            "host": "demo.internal",
            "url": url,
            "user_agent": rng.choice(_USER_AGENTS),
            "status_code": status,
            "response_size": rng.randint(200, 50000),
        }
        records.append(record)

    return records
