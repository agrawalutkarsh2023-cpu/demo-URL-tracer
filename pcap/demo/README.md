# Demo PCAP — Controlled Test Data

This directory contains synthetic PCAP files for testing the PCAP processing pipeline.

---

## What is here

| File | Description |
|---|---|
| `generate_demo_pcap.py` | Script to generate `demo_attacks.pcap` |
| `demo_attacks.pcap` | Generated demo PCAP (run the script to create it) |

---

## Generate the demo PCAP

From the `pcap/` directory:

```bash
python demo/generate_demo_pcap.py
```

This creates `demo/demo_attacks.pcap`.

---

## What the demo PCAP contains

| # | Traffic Type | Source IP | URI Pattern |
|---|---|---|---|
| 1 | Normal GET | 192.168.1.10 | `/index.html` |
| 2 | Normal GET | 192.168.1.10 | `/about` |
| 3 | Normal POST | 192.168.1.10 | `/login` |
| 4 | SQL Injection (demo) | 192.168.1.20 | `/search?id=1' UNION SELECT ...` |
| 5 | SQL Injection (demo) | 192.168.1.20 | `/login?username=admin' OR ...` |
| 6 | XSS (demo) | 192.168.1.30 | `/search?q=<script>...` |
| 7 | XSS (demo) | 192.168.1.30 | `/profile?name=<img onerror=...>` |
| 8 | Directory Traversal (demo) | 192.168.1.40 | `/download?file=../../etc/passwd` |
| 9 | Directory Traversal (demo) | 192.168.1.40 | `/read?path=../../config/...` |
| 10 | Command Injection (demo) | 192.168.1.50 | `/ping?host=127.0.0.1;echo ...` |
| 11 | Command Injection (demo) | 192.168.1.50 | `/exec?cmd=ls -la /etc` |
| 12 | TLS / HTTPS (uninspectable) | 192.168.1.20 | *(encrypted, port 443)* |
| 13 | TLS / HTTPS (uninspectable) | 192.168.1.30 | *(encrypted, port 443)* |

**Expected pipeline output:**
- `packets_processed`: 13
- `http_requests`: 11
- `uninspectable`: 2
- `records`: 11 normalized dicts

---

## Important disclaimer

> All URL strings in this demo PCAP are **inert test data only**.
> They are byte sequences inside a controlled capture file.
> This demo PCAP does **not** execute any attacks.
> It does **not** connect to any real system.
> It is intended purely for demonstrating PCAP parsing.
