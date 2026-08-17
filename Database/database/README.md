# Database Layer — URL-Based Cyber Attack Detection & IP Intelligence System

> **DEMO PROTOTYPE** — All data in this database is **synthetic / simulated**.  
> No real IPDR, credentials, production traffic, or victim data is stored here.

---

## Directory Structure

```
database/
├── schema.sql              # Raw DDL — defines all tables, indexes, constraints
├── seed_demo_data.py       # Creates ~500 synthetic HTTP/attack records
├── reset_demo_database.py  # Drops all data; optionally reseeds
├── db_functions.py         # Clean Python API — all SQL lives here
└── README.md               # This file
```

The actual database file lives in the **backend** folder (auto-created by FastAPI on first run):

```
backend/
└── demo.db                 # SQLite file (gitignored)
```

---

## Tables & Relationships

```
uploads (1) ──────────────> (N) requests
    uploads.id  <──  requests.upload_id

requests (1) ─────────────> (N) detections
    requests.id <──  detections.request_id

requests.source_ip ───────> ip_analysis.ip   (logical aggregate — no FK)
```

### `uploads`

Tracks every file (CSV or PCAP) uploaded to the system.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| filename | TEXT | Original filename |
| file_type | TEXT | `csv` or `pcap` |
| status | TEXT | `pending` \| `processing` \| `completed` \| `error` |
| total_records | INTEGER | Rows parsed from file |
| records_processed | INTEGER | Rows successfully stored |
| attacks_detected | INTEGER | Rows with a detection |
| high_risk_ips | INTEGER | IPs classified HIGH or CRITICAL |
| upload_time | TEXT | ISO-8601 UTC |
| error_message | TEXT | Populated on error only |

### `requests`

One row per HTTP request record.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| timestamp | TEXT | ISO-8601 UTC of captured request |
| source_ip | TEXT | NOT NULL · indexed |
| destination_ip | TEXT | |
| method | TEXT | GET, POST, PUT … |
| host | TEXT | HTTP Host header |
| url | TEXT | Full path + query string |
| user_agent | TEXT | |
| status_code | INTEGER | HTTP response code |
| response_size | INTEGER | Response bytes |
| upload_id | INTEGER FK | → uploads.id |

### `detections`

One row per attack detection event.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| request_id | INTEGER FK | → requests.id (CASCADE DELETE) |
| attack_type | TEXT | SQL Injection, XSS, Command Injection … |
| severity | TEXT | `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL` |
| confidence | REAL | 0.0–1.0 |
| detection_method | TEXT | `RULE` \| `ML` \| `HYBRID` |
| result | TEXT | `ATTEMPT` \| `POTENTIAL_SUCCESS` |
| created_at | TEXT | ISO-8601 UTC |
| source_ip | TEXT | Denormalised snapshot for fast queries |
| url | TEXT | Denormalised snapshot |
| host | TEXT | Denormalised snapshot |

### `ip_analysis`

One row per unique IP — aggregated risk profile.

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ip | TEXT UNIQUE | The IP address |
| total_requests | INTEGER | All requests from this IP |
| attack_count | INTEGER | Requests that triggered detections |
| attack_types | TEXT | JSON array: `["SQL Injection", "XSS"]` |
| risk_score | INTEGER | Composite score (0–∞) |
| risk_level | TEXT | `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL` |
| first_seen | TEXT | ISO-8601 UTC |
| last_seen | TEXT | ISO-8601 UTC |
| geo_country | TEXT | **SIMULATED** — not real IPDR |
| geo_city | TEXT | **SIMULATED** |
| isp | TEXT | **SIMULATED** |
| updated_at | TEXT | ISO-8601 UTC |

---

## Risk Score Thresholds

| Score Range | Risk Level |
|---|---|
| 0–20 | LOW |
| 21–50 | MEDIUM |
| 51–100 | HIGH |
| 101+ | CRITICAL |

---

## Quick Start

### 1. First-time setup (backend manages this automatically)

When you run the FastAPI backend, it auto-creates `demo.db` and seeds it:

```bash
cd backend/
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Manual seed (standalone, no backend required)

```bash
cd database/
python seed_demo_data.py
# → Uses default path: ../backend/demo.db

python seed_demo_data.py --db /custom/path/demo.db --records 800 --verbose
```

### 3. Reset the database

```bash
cd database/

# Interactive prompt — then manual reseed
python reset_demo_database.py

# Skip prompt, reset and reseed in one command
python reset_demo_database.py --yes --reseed

# Reset + reseed with 800 records
python reset_demo_database.py --yes --reseed --records 800 --verbose
```

### 4. Apply raw SQL schema (optional — for direct sqlite3 use)

```bash
sqlite3 ../backend/demo.db < schema.sql
```

---

## Database Functions Reference

Import from `db_functions.py`:

```python
import sqlite3
from db_functions import (
    create_request,
    create_detection,
    get_attacks,
    get_attack_by_id,
    get_ip_analysis,
    get_dashboard_stats,
    save_upload,
    get_upload_status,
    update_upload,
    get_recent_detections,
    get_high_risk_ips,
)

conn = sqlite3.connect("../backend/demo.db")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
```

### `create_request(conn, source_ip, **kwargs) → int`

```python
req_id = create_request(
    conn,
    source_ip="10.0.0.5",
    destination_ip="192.168.100.1",
    method="GET",
    host="demo.internal",
    url="/login?q=test",
    user_agent="Mozilla/5.0",
    status_code=200,
    response_size=4096,
    upload_id=1,
)
```

### `create_detection(conn, request_id, attack_type, severity, confidence, detection_method, result, ...) → int`

```python
det_id = create_detection(
    conn,
    request_id=req_id,
    attack_type="SQL Injection",
    severity="HIGH",
    confidence=0.97,
    detection_method="RULE",
    result="ATTEMPT",
    source_ip="10.0.0.5",
    url="/login?q=test",
    host="demo.internal",
)
```

### `get_attacks(conn, **filters) → list[dict]`

```python
# All SQL Injection attacks
attacks = get_attacks(conn, attack_type="SQL Injection")

# Critical attacks on a specific IP
attacks = get_attacks(conn, severity="CRITICAL", source_ip="10.0.0.5")

# Recent successful attacks
attacks = get_attacks(conn, result="POTENTIAL_SUCCESS", limit=50)

# Date-range filter
attacks = get_attacks(
    conn,
    date_from="2026-08-01T00:00:00",
    date_to="2026-08-18T23:59:59",
)
```

### `get_attack_by_id(conn, detection_id) → dict | None`

```python
detail = get_attack_by_id(conn, 42)
# Returns detection fields + joined request fields (req_timestamp, req_method, etc.)
```

### `get_ip_analysis(conn, ip=None, risk_level=None, min_risk_score=None) → list[dict]`

```python
# Full profile for one IP
profile = get_ip_analysis(conn, ip="10.0.0.5")

# All CRITICAL IPs
critical = get_ip_analysis(conn, risk_level="CRITICAL")

# IPs with score > 50
high = get_ip_analysis(conn, min_risk_score=51)
```

### `get_dashboard_stats(conn) → dict`

```python
stats = get_dashboard_stats(conn)
# Returns:
# {
#   "total_requests": 500,
#   "total_attacks": 45,
#   "high_risk_ips": 7,
#   "critical_ips": 3,
#   "potential_success_count": 24,
#   "attacks_by_type": [{"attack_type": "SQL Injection", "count": 7}, ...],
#   "attacks_by_severity": [{"severity": "HIGH", "count": 30}, ...],
#   "attacks_by_method": [{"detection_method": "RULE", "count": 40}, ...],
#   "top_attacking_ips": [...],
#   "recent_detections": [...],
# }
```

### `save_upload(conn, filename, file_type, status, total_records) → int`

```python
upload_id = save_upload(conn, "traffic.csv", "csv", "processing", 500)
```

### `get_upload_status(conn, upload_id) → dict | None`

```python
status = get_upload_status(conn, upload_id=1)
# {"id": 1, "filename": "...", "status": "completed", "attacks_detected": 45, ...}
```

### `update_upload(conn, upload_id, **kwargs)`

```python
update_upload(conn, upload_id=1, status="completed", attacks_detected=45, high_risk_ips=7)
```

### `get_recent_detections(conn, limit=20) → list[dict]`

```python
recent = get_recent_detections(conn, limit=10)
```

### `get_high_risk_ips(conn, limit=10) → list[dict]`

```python
top_threats = get_high_risk_ips(conn, limit=5)
```

---

## Example Queries (Raw SQL)

### All HIGH/CRITICAL attacks in the last 24 hours

```sql
SELECT d.*, r.method, r.status_code
FROM detections d
JOIN requests r ON d.request_id = r.id
WHERE d.severity IN ('HIGH', 'CRITICAL')
  AND d.created_at >= datetime('now', '-1 day')
ORDER BY d.created_at DESC;
```

### Attack type frequency chart data

```sql
SELECT attack_type, COUNT(*) AS count
FROM detections
GROUP BY attack_type
ORDER BY count DESC;
```

### Top attacking IPs

```sql
SELECT ip, risk_score, risk_level, attack_count, attack_types
FROM ip_analysis
WHERE attack_count > 0
ORDER BY risk_score DESC
LIMIT 10;
```

### Filter by IP and severity

```sql
SELECT * FROM detections
WHERE source_ip = '10.0.0.5'
  AND severity = 'CRITICAL'
ORDER BY created_at DESC;
```

### Dashboard summary counts

```sql
SELECT
    (SELECT COUNT(*) FROM requests)                                      AS total_requests,
    (SELECT COUNT(*) FROM detections)                                    AS total_attacks,
    (SELECT COUNT(*) FROM ip_analysis WHERE risk_level IN ('HIGH','CRITICAL')) AS high_risk_ips,
    (SELECT COUNT(*) FROM detections WHERE result = 'POTENTIAL_SUCCESS') AS potential_hits;
```

### Upload history

```sql
SELECT id, filename, file_type, status, records_processed, attacks_detected, upload_time
FROM uploads
ORDER BY upload_time DESC;
```

---

## Backend Integration

The **FastAPI backend** (`backend/`) uses **SQLAlchemy ORM** directly — it does **not** import `db_functions.py`.  
The ORM models (`backend/models.py`) exactly mirror the schema defined in `schema.sql`.

```
backend/database.py  → SQLAlchemy engine (SQLite)
backend/models.py    → ORM models: Upload, Request, Detection, IPAnalysis
backend/utils/seed.py → ORM-based seed (used at FastAPI startup)
```

`db_functions.py` is intended for:

| Use case | How |
|---|---|
| Standalone seed/reset scripts | `python seed_demo_data.py` |
| ML/data scripts outside FastAPI | `import db_functions` |
| PCAP processing pipeline | `from db_functions import create_request` |
| Jupyter notebooks / demos | `conn = sqlite3.connect("demo.db")` |
| Quick ad-hoc debugging | `python db_functions.py demo.db` |

---

## Data Reset Workflow

```bash
# Full reset + reseed cycle (team demo prep)
cd database/
python reset_demo_database.py --yes --reseed --records 500

# Verify
python db_functions.py ../backend/demo.db
```

---

## Attack Types Covered

| Attack Type | Severity | Detection Method |
|---|---|---|
| SQL Injection | HIGH | RULE / HYBRID |
| XSS | MEDIUM | RULE / HYBRID |
| Directory Traversal | HIGH | RULE / HYBRID |
| Command Injection | CRITICAL | RULE / HYBRID |
| SSRF | HIGH | RULE / HYBRID |
| Brute Force | HIGH | RULE / ML |
| Credential Stuffing | HIGH | RULE / ML |
| XXE | HIGH | RULE |
| Web Shell | CRITICAL | RULE |
| Typosquatting | MEDIUM | RULE |
| HTTP Parameter Pollution | MEDIUM | RULE / ML |

---

> **Note**: This is a hackathon demo prototype. The database is designed to be  
> **simple**, **portable**, **easy to reset**, and **easy to seed** — not for production use.
