"""
generate_demo_pcap.py — Controlled demo PCAP generator.
========================================================

Creates a synthetic .pcap file containing simulated HTTP traffic for
testing the PCAP processing pipeline.

ALL traffic in this file is:
  - Simulated between RFC 1918 private IP addresses (192.168.x.x / 10.x.x.x)
  - Targeting a fictional hostname (demo.target.local)
  - Containing demo URL strings only — NOT executed against any real system
  - Crafted purely as test data for PCAP parsing

IMPORTANT:
  The URL strings containing SQL injection, XSS, traversal, and command
  injection patterns are DEMO EXAMPLES ONLY.
  They are inert byte sequences inside a controlled PCAP file.
  This script does NOT send any network traffic.
  This script does NOT exploit any system.
  This script does NOT connect to any real server.

Usage:
    python demo/generate_demo_pcap.py
    # or from parent directory:
    python -m demo.generate_demo_pcap
"""

import os
import sys
from pathlib import Path

from scapy.all import IP, TCP, Raw, wrpcap

# ---------------------------------------------------------------------------
# Synthetic network topology (all RFC 1918 / fictional addresses)
# ---------------------------------------------------------------------------

SERVER_IP:   str = "10.0.0.1"          # Fictional demo server
SERVER_PORT: int = 80                   # Standard HTTP

# Fictional client IPs — not real systems
_CLIENTS = {
    "normal_user": "192.168.1.10",
    "sqli_source":  "192.168.1.20",
    "xss_source":   "192.168.1.30",
    "traversal":    "192.168.1.40",
    "cmdinject":    "192.168.1.50",
}

HOST = "demo.target.local"             # Fictional hostname


# ---------------------------------------------------------------------------
# Packet builders
# ---------------------------------------------------------------------------

def _make_get(
    src_ip: str,
    uri: str,
    user_agent: str = "DemoBrowser/1.0",
    sport: int = 54321,
) -> object:
    """Build a synthetic HTTP GET request packet."""
    http_raw = (
        f"GET {uri} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Accept: */*\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8")

    return (
        IP(src=src_ip, dst=SERVER_IP, ttl=64) /
        TCP(sport=sport, dport=SERVER_PORT, flags="PA", seq=1000, ack=1) /
        Raw(load=http_raw)
    )


def _make_post(
    src_ip: str,
    uri: str,
    body: str,
    user_agent: str = "DemoBrowser/1.0",
    sport: int = 54321,
) -> object:
    """Build a synthetic HTTP POST request packet."""
    body_bytes = body.encode("utf-8")
    http_raw = (
        f"POST {uri} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return (
        IP(src=src_ip, dst=SERVER_IP, ttl=64) /
        TCP(sport=sport, dport=SERVER_PORT, flags="PA", seq=2000, ack=1) /
        Raw(load=http_raw)
    )


def _make_tls_packet(src_ip: str, sport: int = 54443) -> object:
    """
    Build a synthetic TLS Application Data packet on port 443.

    This represents HTTPS traffic that the PCAP module CANNOT inspect.
    Content-Type 0x17 = Application Data, version 0x0303 = TLS 1.2.
    The payload is fake random bytes — no real encrypted data.
    """
    tls_header  = bytes([0x17, 0x03, 0x03, 0x00, 0x20])
    fake_cipher = b"\xab\xcd\xef\x12" * 8   # Dummy "encrypted" bytes
    return (
        IP(src=src_ip, dst=SERVER_IP, ttl=64) /
        TCP(sport=sport, dport=443, flags="PA", seq=3000, ack=1) /
        Raw(load=tls_header + fake_cipher)
    )


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def create_demo_pcap(output_path: str = None) -> str:
    """
    Generate a controlled demo PCAP file with synthetic HTTP traffic.

    Packet manifest
    ---------------
    #01  Normal GET  — /index.html               (normal_user)
    #02  Normal GET  — /about                    (normal_user)
    #03  Normal POST — /login  (form body)        (normal_user)
    #04  SQL Inj.    — UNION SELECT demo string   (sqli_source)
    #05  SQL Inj.    — OR 1=1  demo string        (sqli_source)
    #06  XSS         — <script> demo string       (xss_source)
    #07  XSS         — <img onerror> demo string  (xss_source)
    #08  Dir Traversal — ../../etc/passwd demo    (traversal)
    #09  Dir Traversal — ../../config demo        (traversal)
    #10  Cmd Inject   — ;echo demo string         (cmdinject)
    #11  Cmd Inject   — ls -la demo string        (cmdinject)
    #12  TLS (HTTPS) — port 443, uninspectable    (sqli_source)
    #13  TLS (HTTPS) — port 443, uninspectable    (xss_source)

    Total: 11 HTTP requests  +  2 TLS (uninspectable)  =  13 packets

    Args:
        output_path: File path for the output .pcap.
                     Defaults to demo/demo_attacks.pcap relative to this file.

    Returns:
        Absolute path to the created PCAP file.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "demo_attacks.pcap")

    packets = []

    # ------------------------------------------------------------------
    # Group 1: Normal HTTP traffic
    # ------------------------------------------------------------------
    packets.append(_make_get(
        _CLIENTS["normal_user"], "/index.html",
        user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0 Safari/537.36",
        sport=54001,
    ))
    packets.append(_make_get(
        _CLIENTS["normal_user"], "/about",
        user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0 Safari/537.36",
        sport=54002,
    ))
    packets.append(_make_post(
        _CLIENTS["normal_user"], "/login",
        body="username=demouser&password=demopass",
        user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0 Safari/537.36",
        sport=54003,
    ))

    # ------------------------------------------------------------------
    # Group 2: SQL Injection demo strings (NOT executed against any system)
    # ------------------------------------------------------------------
    # Pattern: UNION SELECT
    packets.append(_make_get(
        _CLIENTS["sqli_source"],
        "/search?id=1%27%20UNION%20SELECT%20username%2Cpassword%20FROM%20users--",
        user_agent="sqlmap/1.7.8 (demo-only, not real traffic)",
        sport=54010,
    ))
    # Pattern: OR 1=1 bypass
    packets.append(_make_get(
        _CLIENTS["sqli_source"],
        "/login?username=admin%27%20OR%20%271%27%3D%271&password=x",
        user_agent="sqlmap/1.7.8 (demo-only, not real traffic)",
        sport=54011,
    ))

    # ------------------------------------------------------------------
    # Group 3: XSS demo strings (NOT executed against any system)
    # ------------------------------------------------------------------
    # Pattern: <script>alert</script>
    packets.append(_make_get(
        _CLIENTS["xss_source"],
        "/search?q=%3Cscript%3Ealert%28%27demo%27%29%3C%2Fscript%3E",
        user_agent="DemoScanner/1.0",
        sport=54020,
    ))
    # Pattern: <img onerror>
    packets.append(_make_get(
        _CLIENTS["xss_source"],
        "/profile?name=%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E",
        user_agent="DemoScanner/1.0",
        sport=54021,
    ))

    # ------------------------------------------------------------------
    # Group 4: Directory Traversal demo strings (NOT executed)
    # ------------------------------------------------------------------
    # Pattern: ../../etc/passwd
    packets.append(_make_get(
        _CLIENTS["traversal"],
        "/download?file=..%2F..%2F..%2Fetc%2Fpasswd",
        user_agent="curl/7.88.1 (demo)",
        sport=54030,
    ))
    # Pattern: ../../config/secrets
    packets.append(_make_get(
        _CLIENTS["traversal"],
        "/read?path=..%2F..%2Fconfig%2Fsecrets.env",
        user_agent="curl/7.88.1 (demo)",
        sport=54031,
    ))

    # ------------------------------------------------------------------
    # Group 5: Command Injection demo strings (NOT executed)
    # ------------------------------------------------------------------
    # Pattern: ;command after semicolon
    packets.append(_make_get(
        _CLIENTS["cmdinject"],
        "/ping?host=127.0.0.1%3Becho%20DEMO_INJECTION",
        user_agent="python-requests/2.31.0 (demo)",
        sport=54040,
    ))
    # Pattern: ls -la
    packets.append(_make_get(
        _CLIENTS["cmdinject"],
        "/exec?cmd=ls%20-la%20%2Fetc",
        user_agent="python-requests/2.31.0 (demo)",
        sport=54041,
    ))

    # ------------------------------------------------------------------
    # Group 6: TLS / HTTPS — simulated encrypted traffic
    # Counted as uninspectable. NO URL is decoded or fabricated.
    # ------------------------------------------------------------------
    packets.append(_make_tls_packet(_CLIENTS["sqli_source"], sport=54100))
    packets.append(_make_tls_packet(_CLIENTS["xss_source"],  sport=54101))

    # ------------------------------------------------------------------
    # Write to disk
    # ------------------------------------------------------------------
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wrpcap(output_path, packets)

    print(f"\n[+] Demo PCAP generated: {output_path}")
    print(f"[+] Total packets written: {len(packets)}")
    print(f"    Group 1 — Normal requests:              3 packets")
    print(f"    Group 2 — SQL Injection (demo strings): 2 packets")
    print(f"    Group 3 — XSS (demo strings):           2 packets")
    print(f"    Group 4 — Dir Traversal (demo strings): 2 packets")
    print(f"    Group 5 — Cmd Injection (demo strings): 2 packets")
    print(f"    Group 6 — TLS/HTTPS (uninspectable):    2 packets")

    return output_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    create_demo_pcap()
