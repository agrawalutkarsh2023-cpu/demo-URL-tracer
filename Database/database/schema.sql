-- =============================================================================
-- schema.sql
-- URL-Based Cyber Attack Detection & IP Intelligence System
-- DEMO PROTOTYPE — All data stored here is SYNTHETIC / SIMULATED only.
--
-- Technology: SQLite 3
-- Usage:
--   sqlite3 demo.db < schema.sql
-- =============================================================================

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS detections;
DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS ip_analysis;
DROP TABLE IF EXISTS uploads;

-- =============================================================================
-- TABLE: uploads
-- Tracks each file (CSV or PCAP) uploaded to the system.
-- Processing status and aggregate counts are stored here.
-- =============================================================================
CREATE TABLE IF NOT EXISTS uploads (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    filename            TEXT    NOT NULL,
    file_type           TEXT    NOT NULL CHECK(file_type IN ('csv', 'pcap')),
    status              TEXT    NOT NULL DEFAULT 'pending'
                                CHECK(status IN ('pending', 'processing', 'completed', 'error')),
    total_records       INTEGER DEFAULT 0,
    records_processed   INTEGER DEFAULT 0,
    attacks_detected    INTEGER DEFAULT 0,
    high_risk_ips       INTEGER DEFAULT 0,
    upload_time         TEXT    DEFAULT (datetime('now')),
    error_message       TEXT
);

-- =============================================================================
-- TABLE: requests
-- One row per HTTP request record extracted from a CSV or PCAP upload.
-- =============================================================================
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

CREATE INDEX IF NOT EXISTS idx_requests_source_ip  ON requests(source_ip);
CREATE INDEX IF NOT EXISTS idx_requests_timestamp   ON requests(timestamp);
CREATE INDEX IF NOT EXISTS idx_requests_upload_id   ON requests(upload_id);

-- =============================================================================
-- TABLE: detections
-- One row per attack detection event linked to a single request.
-- =============================================================================
CREATE TABLE IF NOT EXISTS detections (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id          INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    attack_type         TEXT    NOT NULL,
    severity            TEXT    NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    confidence          REAL    NOT NULL,
    detection_method    TEXT    NOT NULL CHECK(detection_method IN ('RULE', 'ML', 'HYBRID')),
    result              TEXT    NOT NULL CHECK(result IN ('ATTEMPT', 'POTENTIAL_SUCCESS')),
    created_at          TEXT    DEFAULT (datetime('now')),
    source_ip           TEXT,
    url                 TEXT,
    host                TEXT
);

CREATE INDEX IF NOT EXISTS idx_detections_request_id        ON detections(request_id);
CREATE INDEX IF NOT EXISTS idx_detections_attack_type       ON detections(attack_type);
CREATE INDEX IF NOT EXISTS idx_detections_severity          ON detections(severity);
CREATE INDEX IF NOT EXISTS idx_detections_source_ip         ON detections(source_ip);
CREATE INDEX IF NOT EXISTS idx_detections_result            ON detections(result);
CREATE INDEX IF NOT EXISTS idx_detections_created_at        ON detections(created_at);
CREATE INDEX IF NOT EXISTS idx_detections_detection_method  ON detections(detection_method);

-- =============================================================================
-- TABLE: ip_analysis
-- One row per unique IP address. Aggregates risk score, attack history, etc.
-- =============================================================================
CREATE TABLE IF NOT EXISTS ip_analysis (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ip              TEXT    NOT NULL UNIQUE,
    total_requests  INTEGER DEFAULT 0,
    attack_count    INTEGER DEFAULT 0,
    attack_types    TEXT    DEFAULT '[]',
    risk_score      INTEGER DEFAULT 0,
    risk_level      TEXT    NOT NULL DEFAULT 'LOW'
                            CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    first_seen      TEXT    DEFAULT (datetime('now')),
    last_seen       TEXT,
    geo_country     TEXT    DEFAULT 'Simulated',
    geo_city        TEXT    DEFAULT 'Simulated',
    isp             TEXT    DEFAULT 'Simulated ISP',
    updated_at      TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ip_analysis_risk_level  ON ip_analysis(risk_level);
CREATE INDEX IF NOT EXISTS idx_ip_analysis_risk_score  ON ip_analysis(risk_score DESC);

-- =============================================================================
-- RELATIONSHIPS
--   uploads (1) --> (N) requests       via requests.upload_id
--   requests (1) --> (N) detections    via detections.request_id
--   requests.source_ip --> ip_analysis.ip  (logical aggregate, no FK)
-- =============================================================================
