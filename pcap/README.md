# pcap — PCAP Processing Module

> Part of: **URL-Based Cyber Attack Detection & IP Intelligence System**
> Role: PCAP file ingestion → packet parsing → HTTP extraction → normalized records → backend

---

## What this module does

Reads `.pcap` and `.pcapng` files and returns structured Python data to the backend.

```
PCAP file
    ↓  validate (extension, size, readable)
    ↓  load with Scapy
    ↓  per-packet: extract IP/TCP metadata
    ↓  detect TLS/HTTPS → mark as uninspectable
    ↓  parse HTTP/1.x request line + headers
    ↓  normalize to standard schema
    ↓
process_pcap() → dict
    ↓
Backend detection engine
```

## What this module does NOT do

| Responsibility | Owner |
|---|---|
| Attack classification (SQLi, XSS, …) | `backend/` |
| Risk scoring | `backend/` or `ml_model/` |
| Database writes | `backend/` |
| ML model inference | `ml_model/` |
| REST API / endpoints | `backend/` |
| Frontend / UI | `frontend/` |
| Live packet capture | Not in scope |
| HTTPS decryption | Impossible without keys |

---

## Project structure

```
pcap/
├── __init__.py           ← exposes process_pcap()
├── models.py             ← ProcessingResult, PacketRecord, PCAPError
├── parser.py             ← file validation + Scapy loading
├── extractor.py          ← per-packet IP/HTTP/TLS extraction
├── normalizer.py         ← standard schema output
├── processor.py          ← process_pcap() entry point
├── demo/
│   ├── generate_demo_pcap.py  ← generates demo_attacks.pcap
│   └── README.md
├── tests/
│   └── test_pcap.py     ← full test suite
└── README.md
```

---

## Installation

```bash
pip install scapy
```

No other external dependencies.

---

## Quick start

### 1. Generate the demo PCAP

```bash
cd pcap/
python demo/generate_demo_pcap.py
# → demo/demo_attacks.pcap
```

### 2. Call process_pcap()

```python
from pcap.processor import process_pcap

result = process_pcap("demo/demo_attacks.pcap")

print(result)
```

### 3. Expected output

```json
{
    "status": "COMPLETED",
    "filename": "demo_attacks.pcap",
    "packets_processed": 13,
    "http_requests": 11,
    "inspectable_requests": 11,
    "uninspectable": 2,
    "records": [
        {
            "timestamp": "2026-08-18T00:00:00+00:00",
            "source_ip": "192.168.1.10",
            "destination_ip": "10.0.0.1",
            "source_port": 54001,
            "destination_port": 80,
            "protocol": "IPv4",
            "method": "GET",
            "host": "demo.target.local",
            "url": "http://demo.target.local/index.html",
            "user_agent": "Mozilla/5.0 ...",
            "status_code": null,
            "response_size": null
        }
    ],
    "error": null
}
```

---

## Output schema reference

### Top-level result

| Key | Type | Description |
|---|---|---|
| `status` | `str` | `"COMPLETED"` \| `"ERROR"` \| `"NO_HTTP"` |
| `filename` | `str` | Basename of the input file |
| `packets_processed` | `int` | Total packets iterated |
| `http_requests` | `int` | HTTP requests successfully extracted |
| `inspectable_requests` | `int` | Alias for `http_requests` |
| `uninspectable` | `int` | TLS/HTTPS packets — not decoded |
| `records` | `list[dict]` | Normalized `PacketRecord` dicts |
| `error` | `str \| None` | Error message when `status == "ERROR"` |

### Per-record schema

| Field | Type | Notes |
|---|---|---|
| `timestamp` | `str \| None` | ISO 8601 UTC |
| `source_ip` | `str \| None` | |
| `destination_ip` | `str \| None` | |
| `source_port` | `int \| None` | |
| `destination_port` | `int \| None` | |
| `protocol` | `str \| None` | `"IPv4"` or `"IPv6"` |
| `method` | `str \| None` | `GET`, `POST`, `PUT`, … |
| `host` | `str \| None` | HTTP `Host` header |
| `url` | `str \| None` | `http://{host}{uri}` or just `{uri}` |
| `user_agent` | `str \| None` | HTTP `User-Agent` header |
| `status_code` | `int \| None` | HTTP response code (if captured) |
| `response_size` | `int \| None` | `Content-Length` from response |

> All fields are always present. Missing values are `null` (Python `None`), never omitted.

---

## HTTPS / TLS limitation

> **HTTPS traffic cannot be inspected.**

TLS/HTTPS packets are detected by:
1. Destination or source port is 443 / 8443
2. Raw payload starts with a TLS Content-Type byte (`0x14`–`0x17`) followed by TLS version major `0x03`

When a TLS packet is detected:
- It is **counted** in `uninspectable`
- It does **not** produce a record in `records`
- No URL is fabricated or guessed

This is reported honestly in the result:
```json
{
    "uninspectable": 2,
    "records": []   ← no fake URLs
}
```

---

## Error handling

`process_pcap()` never raises exceptions. All errors return a structured dict:

```json
{
    "status": "ERROR",
    "filename": "bad_file.pcap",
    "error": "File not found: bad_file.pcap",
    "packets_processed": 0,
    "http_requests": 0,
    "inspectable_requests": 0,
    "uninspectable": 0,
    "records": []
}
```

Handled cases:
- File not found
- File not readable (permissions)
- Wrong extension
- Empty file (0 bytes)
- File too large (> 100 MB)
- Corrupted or truncated PCAP (Scapy parse failure)
- PCAP with zero packets
- PCAP with no HTTP traffic (`status: "NO_HTTP"`)
- Malformed packets (silently skipped, counted in `packets_processed`)

---

## Running tests

```powershell
# Windows PowerShell (from inside pcap/)
$env:PYTHONPATH = "C:\path\to\sih"
python -m pytest tests/test_pcap.py -v

# Or as a one-liner from the sih/ parent directory:
$env:PYTHONPATH = $PWD; python -m pytest pcap/tests/test_pcap.py -v
```

```bash
# Linux / macOS / Git Bash (from inside pcap/)
PYTHONPATH=.. python -m pytest tests/test_pcap.py -v
```

All tests use synthetic in-memory Scapy packets — no real network traffic.

> **Note on folder name**: The folder must be named `pcap` (lowercase) for
> `from pcap.processor import process_pcap` to resolve correctly.
> Python's import system is case-sensitive even on Windows.

---

## Backend integration

The backend only needs one import:

```python
from pcap.processor import process_pcap

result = process_pcap(file_path)
# result is a plain Python dict — JSON-serializable

# Forward to detection engine:
for record in result["records"]:
    detection_engine.analyze(record)

# Store metadata:
db.save_scan_metadata(
    filename=result["filename"],
    packets=result["packets_processed"],
    http_requests=result["http_requests"],
    uninspectable=result["uninspectable"],
)
```

The `pcap/` module has no knowledge of:
- The database schema
- The detection engine logic
- The ML model
- The API response format

---

## Demo PCAP disclaimer

The demo PCAP (`demo/demo_attacks.pcap`) contains **inert test strings only**.

URL patterns such as `UNION SELECT`, `<script>`, `../../etc/passwd`, and `;echo` are:
- Controlled byte sequences inside a local file
- Never sent to any real system
- Never executed by this module
- Intended purely for demonstrating PCAP parsing

This module does not perform attacks. It only reads and parses files.
