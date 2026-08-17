"""
db_functions.py
===============
URL-Based Cyber Attack Detection & IP Intelligence System
DEMO PROTOTYPE

Central database access layer built on raw sqlite3 (standard library).
All SQL lives here — no scattered queries in other modules.

⚠ All data in this database is SYNTHETIC / DEMO only.
  No real IPDR, credentials, or victim data is ever stored.

Public API
----------
    create_request(conn, **fields) -> int
    create_detection(conn, **fields) -> int
    get_attacks(conn, **filters) -> list[dict]
    get_attack_by_id(conn, detection_id) -> dict | None
    get_ip_analysis(conn, ip=None, **filters) -> list[dict]
    get_dashboard_stats(conn) -> dict
    save_upload(conn, **fields) -> int
    get_upload_status(conn, upload_id) -> dict | None
    update_upload(conn, upload_id, **fields) -> None
    get_recent_detections(conn, limit=20) -> list[dict]
    get_high_risk_ips(conn, limit=10) -> list[dict]

Usage (standalone — no SQLAlchemy required)
------------------------------------------
    import sqlite3
    from db_functions import create_request, get_dashboard_stats

    conn = sqlite3.connect("../backend/demo.db")
    conn.row_factory = sqlite3.Row      # enables dict-like row access
    conn.execute("PRAGMA foreign_keys = ON")

    req_id = create_request(conn, source_ip="10.0.0.5", url="/login")
    stats  = get_dashboard_stats(conn)
    conn.close()

Integration with FastAPI / SQLAlchemy backend
---------------------------------------------
The FastAPI backend already uses SQLAlchemy ORM (backend/database.py).
These functions are provided as a STANDALONE alternative — useful for:
  • The standalone seed / reset scripts
  • Data science / ML notebooks
  • Quick ad-hoc queries without importing the full ORM stack
  • PCAP / CSV processing scripts that run outside FastAPI
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    """Convert a sqlite3.Row (or plain tuple) to a dict."""
    if row is None:
        return {}
    if isinstance(row, sqlite3.Row):
        return dict(row)
    return dict(row)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# requests table
# ─────────────────────────────────────────────────────────────────────────────

def create_request(
    conn: sqlite3.Connection,
    source_ip: str,
    timestamp: Optional[str] = None,
    destination_ip: Optional[str] = None,
    method: Optional[str] = None,
    host: Optional[str] = None,
    url: Optional[str] = None,
    user_agent: Optional[str] = None,
    status_code: Optional[int] = None,
    response_size: Optional[int] = None,
    upload_id: Optional[int] = None,
) -> int:
    """
    Insert a new HTTP request record.

    Returns
    -------
    int : the new row id (requests.id)
    """
    cur = conn.execute(
        """INSERT INTO requests
           (timestamp, source_ip, destination_ip, method, host, url,
            user_agent, status_code, response_size, upload_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            timestamp or _now_iso(),
            source_ip,
            destination_ip,
            method,
            host,
            url,
            user_agent,
            status_code,
            response_size,
            upload_id,
        ),
    )
    conn.commit()
    return cur.lastrowid


# ─────────────────────────────────────────────────────────────────────────────
# detections table
# ─────────────────────────────────────────────────────────────────────────────

def create_detection(
    conn: sqlite3.Connection,
    request_id: int,
    attack_type: str,
    severity: str,
    confidence: float,
    detection_method: str,
    result: str,
    source_ip: Optional[str] = None,
    url: Optional[str] = None,
    host: Optional[str] = None,
) -> int:
    """
    Insert a new detection record linked to a request.

    Parameters
    ----------
    severity          : LOW | MEDIUM | HIGH | CRITICAL
    detection_method  : RULE | ML | HYBRID
    result            : ATTEMPT | POTENTIAL_SUCCESS

    Returns
    -------
    int : the new row id (detections.id)
    """
    cur = conn.execute(
        """INSERT INTO detections
           (request_id, attack_type, severity, confidence,
            detection_method, result, source_ip, url, host)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            request_id,
            attack_type,
            severity.upper(),
            confidence,
            detection_method.upper(),
            result.upper(),
            source_ip,
            url,
            host,
        ),
    )
    conn.commit()
    return cur.lastrowid


# ─────────────────────────────────────────────────────────────────────────────
# Query: attacks / detections
# ─────────────────────────────────────────────────────────────────────────────

def get_attacks(
    conn: sqlite3.Connection,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    result: Optional[str] = None,
    source_ip: Optional[str] = None,
    detection_method: Optional[str] = None,
    date_from: Optional[str] = None,   # ISO-8601 string, inclusive
    date_to: Optional[str] = None,     # ISO-8601 string, inclusive
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """
    Return detections matching optional filter criteria.

    Supported filters
    -----------------
    attack_type       : partial case-insensitive match
    severity          : exact match (LOW | MEDIUM | HIGH | CRITICAL)
    result            : exact match (ATTEMPT | POTENTIAL_SUCCESS)
    source_ip         : exact match
    detection_method  : exact match (RULE | ML | HYBRID)
    date_from/date_to : ISO timestamp range on created_at

    Returns
    -------
    list of dicts, ordered by created_at DESC
    """
    sql = "SELECT * FROM detections WHERE 1=1"
    params: list[Any] = []

    if attack_type:
        sql += " AND LOWER(attack_type) LIKE ?"
        params.append(f"%{attack_type.lower()}%")

    if severity:
        sql += " AND severity = ?"
        params.append(severity.upper())

    if result:
        sql += " AND result = ?"
        params.append(result.upper())

    if source_ip:
        sql += " AND source_ip = ?"
        params.append(source_ip)

    if detection_method:
        sql += " AND detection_method = ?"
        params.append(detection_method.upper())

    if date_from:
        sql += " AND created_at >= ?"
        params.append(date_from)

    if date_to:
        sql += " AND created_at <= ?"
        params.append(date_to)

    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_attack_by_id(conn: sqlite3.Connection, detection_id: int) -> Optional[dict]:
    """
    Fetch a single detection record by its primary key,
    joined with its parent request.

    Returns
    -------
    dict with detection + request fields, or None if not found.
    """
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """SELECT
               d.*,
               r.timestamp       AS req_timestamp,
               r.destination_ip  AS req_destination_ip,
               r.method          AS req_method,
               r.user_agent      AS req_user_agent,
               r.status_code     AS req_status_code,
               r.response_size   AS req_response_size
           FROM detections d
           LEFT JOIN requests r ON d.request_id = r.id
           WHERE d.id = ?""",
        (detection_id,),
    ).fetchone()
    return _row_to_dict(row) if row else None


# ─────────────────────────────────────────────────────────────────────────────
# Query: ip_analysis
# ─────────────────────────────────────────────────────────────────────────────

def get_ip_analysis(
    conn: sqlite3.Connection,
    ip: Optional[str] = None,
    risk_level: Optional[str] = None,
    min_risk_score: Optional[int] = None,
    limit: int = 200,
) -> list[dict]:
    """
    Return ip_analysis records.

    If `ip` is provided, returns the single matching record (list of 1 or 0).
    Otherwise returns all IPs matching the optional filters.

    Filters
    -------
    risk_level      : exact match (LOW | MEDIUM | HIGH | CRITICAL)
    min_risk_score  : minimum risk score (inclusive)
    limit           : max rows returned (default 200)

    Returns
    -------
    list of dicts, ordered by risk_score DESC
    """
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM ip_analysis WHERE 1=1"
    params: list[Any] = []

    if ip:
        sql += " AND ip = ?"
        params.append(ip)

    if risk_level:
        sql += " AND risk_level = ?"
        params.append(risk_level.upper())

    if min_risk_score is not None:
        sql += " AND risk_score >= ?"
        params.append(min_risk_score)

    sql += " ORDER BY risk_score DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    result = []
    for r in rows:
        d = _row_to_dict(r)
        # Deserialise attack_types JSON string to list for convenience
        try:
            d["attack_types"] = json.loads(d.get("attack_types") or "[]")
        except (json.JSONDecodeError, TypeError):
            d["attack_types"] = []
        result.append(d)
    return result


def get_high_risk_ips(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    """
    Return top N IPs by risk score with risk level HIGH or CRITICAL.

    Returns
    -------
    list of dicts, ordered by risk_score DESC
    """
    return get_ip_analysis(
        conn,
        risk_level=None,
        min_risk_score=51,  # score > 50 → HIGH or CRITICAL
        limit=limit,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Query: dashboard statistics
# ─────────────────────────────────────────────────────────────────────────────

def get_dashboard_stats(conn: sqlite3.Connection) -> dict:
    """
    Aggregate statistics for the frontend dashboard.

    Returns
    -------
    dict with keys:
        total_requests          int
        total_attacks           int
        high_risk_ips           int
        critical_ips            int
        potential_success_count int
        attacks_by_type         list[{"attack_type": str, "count": int}]
        attacks_by_severity     list[{"severity": str, "count": int}]
        attacks_by_method       list[{"detection_method": str, "count": int}]
        top_attacking_ips       list[{"ip": str, "risk_score": int, ...}]
        recent_detections       list[dict]  (20 most recent)
    """
    conn.row_factory = sqlite3.Row

    total_requests = conn.execute(
        "SELECT COUNT(*) FROM requests"
    ).fetchone()[0]

    total_attacks = conn.execute(
        "SELECT COUNT(*) FROM detections"
    ).fetchone()[0]

    high_risk_ips = conn.execute(
        "SELECT COUNT(*) FROM ip_analysis WHERE risk_level IN ('HIGH', 'CRITICAL')"
    ).fetchone()[0]

    critical_ips = conn.execute(
        "SELECT COUNT(*) FROM ip_analysis WHERE risk_level = 'CRITICAL'"
    ).fetchone()[0]

    potential_success_count = conn.execute(
        "SELECT COUNT(*) FROM detections WHERE result = 'POTENTIAL_SUCCESS'"
    ).fetchone()[0]

    # Attacks grouped by type
    type_rows = conn.execute(
        """SELECT attack_type, COUNT(*) AS count
           FROM detections
           GROUP BY attack_type
           ORDER BY count DESC"""
    ).fetchall()
    attacks_by_type = [{"attack_type": r["attack_type"], "count": r["count"]}
                       for r in type_rows]

    # Attacks grouped by severity
    sev_rows = conn.execute(
        """SELECT severity, COUNT(*) AS count
           FROM detections
           GROUP BY severity
           ORDER BY count DESC"""
    ).fetchall()
    attacks_by_severity = [{"severity": r["severity"], "count": r["count"]}
                           for r in sev_rows]

    # Attacks grouped by detection method
    method_rows = conn.execute(
        """SELECT detection_method, COUNT(*) AS count
           FROM detections
           GROUP BY detection_method
           ORDER BY count DESC"""
    ).fetchall()
    attacks_by_method = [{"detection_method": r["detection_method"], "count": r["count"]}
                         for r in method_rows]

    # Top 10 attacking IPs by risk score
    top_rows = conn.execute(
        """SELECT ip, risk_score, risk_level, attack_count, total_requests, attack_types
           FROM ip_analysis
           WHERE attack_count > 0
           ORDER BY risk_score DESC
           LIMIT 10"""
    ).fetchall()
    top_attacking_ips = []
    for r in top_rows:
        d = _row_to_dict(r)
        try:
            d["attack_types"] = json.loads(d.get("attack_types") or "[]")
        except (json.JSONDecodeError, TypeError):
            d["attack_types"] = []
        top_attacking_ips.append(d)

    # 20 most recent detections
    recent_detections = get_recent_detections(conn, limit=20)

    return {
        "total_requests": total_requests,
        "total_attacks": total_attacks,
        "high_risk_ips": high_risk_ips,
        "critical_ips": critical_ips,
        "potential_success_count": potential_success_count,
        "attacks_by_type": attacks_by_type,
        "attacks_by_severity": attacks_by_severity,
        "attacks_by_method": attacks_by_method,
        "top_attacking_ips": top_attacking_ips,
        "recent_detections": recent_detections,
    }


def get_recent_detections(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    """
    Return the N most recent detection events.

    Returns
    -------
    list of dicts, ordered by created_at DESC
    """
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT * FROM detections
           ORDER BY created_at DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# uploads table
# ─────────────────────────────────────────────────────────────────────────────

def save_upload(
    conn: sqlite3.Connection,
    filename: str,
    file_type: str,
    status: str = "pending",
    total_records: int = 0,
) -> int:
    """
    Create a new upload record and return its id.

    Parameters
    ----------
    file_type : 'csv' or 'pcap'
    status    : 'pending' | 'processing' | 'completed' | 'error'

    Returns
    -------
    int : uploads.id
    """
    cur = conn.execute(
        """INSERT INTO uploads
           (filename, file_type, status, total_records, upload_time)
           VALUES (?, ?, ?, ?, ?)""",
        (filename, file_type.lower(), status, total_records, _now_iso()),
    )
    conn.commit()
    return cur.lastrowid


def get_upload_status(conn: sqlite3.Connection, upload_id: int) -> Optional[dict]:
    """
    Return the current status and processing counts for an upload.

    Returns
    -------
    dict or None if upload_id not found.
    """
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM uploads WHERE id = ?", (upload_id,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def update_upload(
    conn: sqlite3.Connection,
    upload_id: int,
    status: Optional[str] = None,
    records_processed: Optional[int] = None,
    attacks_detected: Optional[int] = None,
    high_risk_ips: Optional[int] = None,
    total_records: Optional[int] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Update mutable fields on an upload record.
    Only non-None arguments are written.
    """
    fields = {}
    if status is not None:
        fields["status"] = status
    if records_processed is not None:
        fields["records_processed"] = records_processed
    if attacks_detected is not None:
        fields["attacks_detected"] = attacks_detected
    if high_risk_ips is not None:
        fields["high_risk_ips"] = high_risk_ips
    if total_records is not None:
        fields["total_records"] = total_records
    if error_message is not None:
        fields["error_message"] = error_message

    if not fields:
        return

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [upload_id]
    conn.execute(f"UPDATE uploads SET {set_clause} WHERE id = ?", values)
    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Example usage / quick smoke test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "../backend/demo.db"

    print(f"Running quick smoke test against: {db_path}\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    stats = get_dashboard_stats(conn)
    print("=== Dashboard Stats ===")
    print(f"  Total requests  : {stats['total_requests']}")
    print(f"  Total attacks   : {stats['total_attacks']}")
    print(f"  High-risk IPs   : {stats['high_risk_ips']}")
    print(f"  Critical IPs    : {stats['critical_ips']}")
    print(f"  Potential hits  : {stats['potential_success_count']}")
    print()
    print("  Attacks by type:")
    for row in stats["attacks_by_type"]:
        print(f"    {row['attack_type']:<30} {row['count']}")
    print()
    print("  Attacks by severity:")
    for row in stats["attacks_by_severity"]:
        print(f"    {row['severity']:<12} {row['count']}")
    print()

    high_risk = get_high_risk_ips(conn, limit=5)
    print("=== Top High-Risk IPs ===")
    for ip in high_risk:
        print(f"  {ip['ip']:<20} score={ip['risk_score']:>4}  "
              f"level={ip['risk_level']:<8}  attacks={ip['attack_count']}")

    conn.close()
    print("\nSmoke test complete.")
