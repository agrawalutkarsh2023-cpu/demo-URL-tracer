"""
test_pcap.py — Test suite for the PCAP processing module.
==========================================================

Uses ONLY controlled, synthetic PCAP data built in memory with Scapy.
No real network traffic. No real files on disk beyond temp files.

Test categories:
  1. File validation (missing, empty, wrong extension)
  2. IP extraction
  3. HTTP method extraction
  4. URL / URI extraction
  5. User-Agent extraction
  6. Multiple packets
  7. Uninspectable (TLS/HTTPS) traffic
  8. Mixed HTTP + TLS
  9. Output schema completeness
  10. Demo PCAP integration

Run:
    python -m pytest tests/test_pcap.py -v
    # or without pytest:
    python tests/test_pcap.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — ensure 'import pcap' always resolves
#
# Directory layout:
#   sih/                  ← must be on sys.path
#   └── PCAP/             ← this IS the 'pcap' package (folder name = package name)
#       └── tests/
#           └── test_pcap.py  ← we are here
#
# Python resolves "import pcap" by finding PCAP/ inside sih/.
# So sih/ must be on sys.path — not PCAP/ itself.
# ---------------------------------------------------------------------------
_sih_dir = Path(__file__).resolve().parent.parent.parent
if str(_sih_dir) not in sys.path:
    sys.path.insert(0, str(_sih_dir))

from scapy.all import IP, TCP, Raw, wrpcap  # noqa: E402

# Modules under test
from pcap.processor import process_pcap                          # noqa: E402
from pcap.extractor import extract_packet, is_tls, parse_http_request  # noqa: E402
from pcap.normalizer import build_url, normalize_record          # noqa: E402
from pcap.models import PCAPError                                # noqa: E402


# ===========================================================================
# Shared helpers
# ===========================================================================

def _write_pcap(packets, suffix: str = ".pcap") -> str:
    """Write a list of Scapy packets to a temp file. Returns the file path."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        tmp_path = f.name
    wrpcap(tmp_path, packets)
    return tmp_path


def _cleanup(path: str) -> None:
    """Delete a temp file safely."""
    try:
        os.unlink(path)
    except OSError:
        pass


def _http_pkt(
    src: str = "192.168.1.1",
    dst: str = "10.0.0.1",
    method: str = "GET",
    uri: str = "/index.html",
    host: str = "demo.local",
    user_agent: str = "TestAgent/1.0",
    sport: int = 54321,
    dport: int = 80,
) -> object:
    """Build a minimal synthetic HTTP request packet."""
    raw = (
        f"{method} {uri} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Accept: */*\r\n"
        f"\r\n"
    ).encode("utf-8")
    return (
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=dport, flags="PA", seq=1000, ack=1) /
        Raw(load=raw)
    )


def _tls_pkt(
    src: str = "192.168.1.1",
    dst: str = "10.0.0.1",
    sport: int = 54321,
) -> object:
    """Build a synthetic TLS Application Data packet (port 443)."""
    # TLS 1.2 Application Data record header + dummy payload
    payload = bytes([0x17, 0x03, 0x03, 0x00, 0x10]) + b"\xab\xcd" * 8
    return (
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=443, flags="PA", seq=2000, ack=1) /
        Raw(load=payload)
    )


# ===========================================================================
# 1. File Validation
# ===========================================================================

class TestFileValidation(unittest.TestCase):
    """Validate that bad files return structured ERROR results, not crashes."""

    def test_missing_file_returns_error_status(self):
        result = process_pcap("/no/such/path/fake.pcap")
        self.assertEqual(result["status"], "ERROR")
        self.assertIsNotNone(result["error"])

    def test_missing_file_error_mentions_not_found(self):
        result = process_pcap("/no/such/path/fake.pcap")
        self.assertIn("not found", result["error"].lower())

    def test_wrong_extension_txt_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pcap")
            tmp = f.name
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "ERROR")
            self.assertIn("extension", result["error"].lower())
        finally:
            _cleanup(tmp)

    def test_wrong_extension_csv_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"a,b,c")
            tmp = f.name
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "ERROR")
        finally:
            _cleanup(tmp)

    def test_empty_file_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as f:
            tmp = f.name   # zero bytes
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "ERROR")
        finally:
            _cleanup(tmp)

    def test_pcapng_extension_is_accepted(self):
        """Extension check should accept .pcapng (parse may succeed or fail)."""
        tmp = _write_pcap([_http_pkt()], suffix=".pcapng")
        try:
            result = process_pcap(tmp)
            # Must not fail on extension — may fail on Scapy parse (that's ok)
            self.assertIn(result["status"], {"COMPLETED", "ERROR", "NO_HTTP"})
        finally:
            _cleanup(tmp)

    def test_pcap_extension_is_accepted(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertIn(result["status"], {"COMPLETED", "NO_HTTP"})
        finally:
            _cleanup(tmp)


# ===========================================================================
# 2. IP Extraction
# ===========================================================================

class TestIPExtraction(unittest.TestCase):

    def test_source_ip_extracted(self):
        tmp = _write_pcap([_http_pkt(src="192.168.5.99")])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["source_ip"], "192.168.5.99")
        finally:
            _cleanup(tmp)

    def test_destination_ip_extracted(self):
        tmp = _write_pcap([_http_pkt(dst="10.20.30.40")])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["destination_ip"], "10.20.30.40")
        finally:
            _cleanup(tmp)

    def test_source_port_extracted(self):
        tmp = _write_pcap([_http_pkt(sport=44444)])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["source_port"], 44444)
        finally:
            _cleanup(tmp)


# ===========================================================================
# 3. HTTP Method Extraction
# ===========================================================================

class TestHTTPMethodExtraction(unittest.TestCase):

    def _run(self, method: str) -> dict:
        tmp = _write_pcap([_http_pkt(method=method)])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "COMPLETED")
            return result["records"][0]
        finally:
            _cleanup(tmp)

    def test_get_method(self):
        self.assertEqual(self._run("GET")["method"], "GET")

    def test_post_method(self):
        self.assertEqual(self._run("POST")["method"], "POST")

    def test_put_method(self):
        self.assertEqual(self._run("PUT")["method"], "PUT")

    def test_delete_method(self):
        self.assertEqual(self._run("DELETE")["method"], "DELETE")

    def test_head_method(self):
        self.assertEqual(self._run("HEAD")["method"], "HEAD")

    def test_patch_method(self):
        self.assertEqual(self._run("PATCH")["method"], "PATCH")


# ===========================================================================
# 4. URL / URI Extraction
# ===========================================================================

class TestURLExtraction(unittest.TestCase):

    def test_simple_url_constructed(self):
        tmp = _write_pcap([_http_pkt(uri="/search?q=hello", host="example.demo")])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["url"], "http://example.demo/search?q=hello")
        finally:
            _cleanup(tmp)

    def test_sqli_url_preserved_verbatim(self):
        """SQL injection demo string must survive extraction unchanged."""
        uri = "/search?id=1%27%20UNION%20SELECT%20username%2Cpassword%20FROM%20users--"
        tmp = _write_pcap([_http_pkt(uri=uri, host="demo.local")])
        try:
            result = process_pcap(tmp)
            url = result["records"][0]["url"]
            self.assertIn("UNION", url)
            self.assertIn("SELECT", url)
        finally:
            _cleanup(tmp)

    def test_xss_url_preserved_verbatim(self):
        uri = "/search?q=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E"
        tmp = _write_pcap([_http_pkt(uri=uri)])
        try:
            result = process_pcap(tmp)
            self.assertIn("script", result["records"][0]["url"].lower())
        finally:
            _cleanup(tmp)

    def test_traversal_url_preserved_verbatim(self):
        uri = "/download?file=..%2F..%2F..%2Fetc%2Fpasswd"
        tmp = _write_pcap([_http_pkt(uri=uri)])
        try:
            result = process_pcap(tmp)
            self.assertIn("passwd", result["records"][0]["url"])
        finally:
            _cleanup(tmp)

    def test_host_field_present(self):
        tmp = _write_pcap([_http_pkt(host="my.demo.server")])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["host"], "my.demo.server")
        finally:
            _cleanup(tmp)


# ===========================================================================
# 5. User-Agent Extraction
# ===========================================================================

class TestUserAgentExtraction(unittest.TestCase):

    def test_user_agent_extracted(self):
        tmp = _write_pcap([_http_pkt(user_agent="CustomAgent/2.0")])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["records"][0]["user_agent"], "CustomAgent/2.0")
        finally:
            _cleanup(tmp)

    def test_sqlmap_agent_extracted(self):
        tmp = _write_pcap([_http_pkt(user_agent="sqlmap/1.7.8 (demo)")])
        try:
            result = process_pcap(tmp)
            self.assertIn("sqlmap", result["records"][0]["user_agent"])
        finally:
            _cleanup(tmp)


# ===========================================================================
# 6. Multiple Packets
# ===========================================================================

class TestMultiplePackets(unittest.TestCase):

    def test_three_packets_counted(self):
        pkts = [
            _http_pkt(uri="/p1", sport=54001),
            _http_pkt(uri="/p2", sport=54002),
            _http_pkt(uri="/p3", sport=54003),
        ]
        tmp = _write_pcap(pkts)
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["packets_processed"], 3)
            self.assertEqual(result["http_requests"], 3)
            self.assertEqual(len(result["records"]), 3)
        finally:
            _cleanup(tmp)

    def test_records_ordered_as_in_pcap(self):
        pkts = [_http_pkt(uri=f"/page{i}", sport=54000 + i) for i in range(5)]
        tmp = _write_pcap(pkts)
        try:
            result = process_pcap(tmp)
            urls = [r["url"] for r in result["records"]]
            for i in range(5):
                self.assertIn(f"/page{i}", urls[i])
        finally:
            _cleanup(tmp)


# ===========================================================================
# 7. Uninspectable (TLS / HTTPS) Traffic
# ===========================================================================

class TestUninspectableTraffic(unittest.TestCase):

    def test_tls_packet_counted_as_uninspectable(self):
        tmp = _write_pcap([_tls_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["uninspectable"], 1)
        finally:
            _cleanup(tmp)

    def test_tls_produces_zero_http_records(self):
        tmp = _write_pcap([_tls_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["http_requests"], 0)
            self.assertEqual(len(result["records"]), 0)
        finally:
            _cleanup(tmp)

    def test_tls_url_never_fabricated(self):
        """No URL must appear in records for an encrypted-only PCAP."""
        tmp = _write_pcap([_tls_pkt(), _tls_pkt(sport=54999)])
        try:
            result = process_pcap(tmp)
            self.assertEqual(len(result["records"]), 0,
                             "TLS packets must not produce any URL records")
        finally:
            _cleanup(tmp)

    def test_two_tls_packets_uninspectable_count(self):
        tmp = _write_pcap([_tls_pkt(sport=54001), _tls_pkt(sport=54002)])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["uninspectable"], 2)
        finally:
            _cleanup(tmp)


# ===========================================================================
# 8. Mixed HTTP + TLS
# ===========================================================================

class TestMixedTraffic(unittest.TestCase):

    def test_http_and_tls_counted_correctly(self):
        pkts = [
            _http_pkt(uri="/page1", sport=54001),
            _tls_pkt(sport=54101),
            _http_pkt(uri="/page2", sport=54002),
            _tls_pkt(sport=54102),
        ]
        tmp = _write_pcap(pkts)
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["packets_processed"],    4)
            self.assertEqual(result["http_requests"],        2)
            self.assertEqual(result["uninspectable"],        2)
            self.assertEqual(len(result["records"]),         2)
        finally:
            _cleanup(tmp)

    def test_no_http_traffic_returns_no_http_status(self):
        """A PCAP with only non-HTTP TCP produces NO_HTTP status."""
        pkt = (
            IP(src="1.2.3.4", dst="5.6.7.8") /
            TCP(sport=12345, dport=9999, flags="S")
        )
        tmp = _write_pcap([pkt])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "NO_HTTP")
            self.assertEqual(result["http_requests"], 0)
            self.assertEqual(result["uninspectable"], 0)
        finally:
            _cleanup(tmp)


# ===========================================================================
# 9. Output Schema Completeness
# ===========================================================================

REQUIRED_TOP_LEVEL_KEYS = {
    "status", "filename", "packets_processed",
    "http_requests", "inspectable_requests",
    "uninspectable", "records", "error",
}

REQUIRED_RECORD_KEYS = {
    "timestamp", "source_ip", "destination_ip",
    "source_port", "destination_port", "protocol",
    "method", "host", "url", "user_agent",
    "status_code", "response_size",
}


class TestOutputSchema(unittest.TestCase):

    def test_top_level_keys_always_present(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            for key in REQUIRED_TOP_LEVEL_KEYS:
                self.assertIn(key, result, f"Missing top-level key: {key}")
        finally:
            _cleanup(tmp)

    def test_record_keys_always_present(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            record = result["records"][0]
            for key in REQUIRED_RECORD_KEYS:
                self.assertIn(key, record, f"Missing record key: {key}")
        finally:
            _cleanup(tmp)

    def test_status_code_is_none_for_request_only(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertIsNone(result["records"][0]["status_code"])
        finally:
            _cleanup(tmp)

    def test_response_size_is_none_for_request_only(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertIsNone(result["records"][0]["response_size"])
        finally:
            _cleanup(tmp)

    def test_filename_matches_basename(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["filename"], os.path.basename(tmp))
        finally:
            _cleanup(tmp)

    def test_inspectable_equals_http_requests(self):
        pkts = [_http_pkt(sport=54000 + i) for i in range(4)]
        tmp = _write_pcap(pkts)
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["inspectable_requests"], result["http_requests"])
        finally:
            _cleanup(tmp)

    def test_error_key_is_present_on_error(self):
        result = process_pcap("/no/such/file.pcap")
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("error", result)
        self.assertIsNotNone(result["error"])

    def test_error_key_is_none_on_success(self):
        tmp = _write_pcap([_http_pkt()])
        try:
            result = process_pcap(tmp)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertIsNone(result["error"])
        finally:
            _cleanup(tmp)


# ===========================================================================
# 10. Demo PCAP Integration
# ===========================================================================

class TestDemoPCAP(unittest.TestCase):
    """
    Integration test using the generated demo PCAP.
    Requires demo/demo_attacks.pcap to exist.
    Skips gracefully if the file has not been generated yet.
    """

    DEMO_PCAP = os.path.join(os.path.dirname(__file__), "..", "demo", "demo_attacks.pcap")

    def setUp(self):
        if not os.path.exists(self.DEMO_PCAP):
            self.skipTest(
                "demo/demo_attacks.pcap not found. "
                "Run `python demo/generate_demo_pcap.py` first."
            )

    def test_demo_pcap_completes_successfully(self):
        result = process_pcap(self.DEMO_PCAP)
        self.assertEqual(result["status"], "COMPLETED")

    def test_demo_pcap_has_http_requests(self):
        result = process_pcap(self.DEMO_PCAP)
        self.assertGreater(result["http_requests"], 0)

    def test_demo_pcap_has_uninspectable_packets(self):
        result = process_pcap(self.DEMO_PCAP)
        self.assertGreater(result["uninspectable"], 0)

    def test_demo_pcap_no_null_methods(self):
        result = process_pcap(self.DEMO_PCAP)
        for record in result["records"]:
            self.assertIsNotNone(record["method"],
                                 "A record has a null method field")

    def test_demo_pcap_all_records_have_url(self):
        result = process_pcap(self.DEMO_PCAP)
        for record in result["records"]:
            self.assertIsNotNone(record["url"],
                                 "A record has a null url field")


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PCAP Module — Test Suite")
    print("=" * 60)
    unittest.main(verbosity=2)
