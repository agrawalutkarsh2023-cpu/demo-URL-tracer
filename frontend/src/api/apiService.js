// ──────────────────────────────────────────────────────────────────────────────
// Central API Service
// Set USE_MOCK = false to use a real backend at BACKEND_URL
// ──────────────────────────────────────────────────────────────────────────────

import {
  mockAttacks,
  mockDashboard,
  mockIPProfiles,
  mockPCAPResult,
  getExportData,
} from '../mock/mockData.js';

const USE_MOCK = true; // ← Flip to false when backend is ready
const BACKEND_URL = '/api'; // Proxied to http://localhost:8000 via vite.config

// Simulate a network delay for a realistic feel
const delay = (ms = 500) => new Promise(res => setTimeout(res, ms));

// ─── Helper ────────────────────────────────────────────────────────────────────
async function request(path, options = {}) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json();
}

// ─── Dashboard ─────────────────────────────────────────────────────────────────
/**
 * GET /api/dashboard
 * Returns summary stats for the dashboard.
 */
export async function getDashboard() {
  if (USE_MOCK) { await delay(400); return mockDashboard; }
  return request('/dashboard');
}

// ─── Attacks ───────────────────────────────────────────────────────────────────
/**
 * GET /api/attacks
 * Returns list of attacks, optionally filtered.
 * @param {Object} filters - { attack_type, severity, result, source_ip, date_from, date_to }
 */
export async function getAttacks(filters = {}) {
  if (USE_MOCK) {
    await delay(350);
    let results = [...mockAttacks];
    if (filters.attack_type && filters.attack_type !== 'ALL')
      results = results.filter(a => a.attack_type === filters.attack_type);
    if (filters.severity && filters.severity !== 'ALL')
      results = results.filter(a => a.severity === filters.severity);
    if (filters.result && filters.result !== 'ALL')
      results = results.filter(a => a.result === filters.result);
    if (filters.source_ip)
      results = results.filter(a => a.source_ip.includes(filters.source_ip));
    if (filters.search)
      results = results.filter(a =>
        a.attack_type.toLowerCase().includes(filters.search.toLowerCase()) ||
        a.source_ip.includes(filters.search) ||
        a.target_url.toLowerCase().includes(filters.search.toLowerCase())
      );
    return results;
  }
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
  );
  return request(`/attacks?${params}`);
}

/**
 * GET /api/attacks/:id
 * Returns a single attack by ID.
 */
export async function getAttackById(id) {
  if (USE_MOCK) {
    await delay(200);
    const attack = mockAttacks.find(a => a.id === id);
    if (!attack) throw new Error('Attack not found');
    return attack;
  }
  return request(`/attacks/${id}`);
}

// ─── IPs ───────────────────────────────────────────────────────────────────────
/**
 * GET /api/ips
 * Returns list of all tracked IP profiles.
 */
export async function getIPs() {
  if (USE_MOCK) {
    await delay(300);
    return Object.values(mockIPProfiles);
  }
  return request('/ips');
}

/**
 * GET /api/ips/:ip
 * Returns profile for a specific IP address.
 */
export async function getIPDetail(ip) {
  if (USE_MOCK) {
    await delay(400);
    const profile = mockIPProfiles[ip];
    if (!profile) throw new Error(`No data found for IP: ${ip}`);
    return {
      ...profile,
      attacks: mockAttacks.filter(a => a.source_ip === ip),
    };
  }
  return request(`/ips/${encodeURIComponent(ip)}`);
}

// ─── File Uploads ──────────────────────────────────────────────────────────────
/**
 * POST /api/upload/csv
 * Uploads a CSV file for analysis.
 */
export async function uploadCSV(file) {
  if (USE_MOCK) {
    await delay(1500);
    return { success: true, message: 'CSV processed (simulated)', attacks_found: 12 };
  }
  const form = new FormData();
  form.append('file', file);
  return request('/upload/csv', {
    method: 'POST',
    headers: {},
    body: form,
  });
}

/**
 * POST /api/upload/pcap
 * Uploads a PCAP file for analysis.
 */
export async function uploadPCAP(file) {
  if (USE_MOCK) {
    // Simulate processing stages
    await delay(2800);
    return mockPCAPResult;
  }
  const form = new FormData();
  form.append('file', file);
  return request('/upload/pcap', {
    method: 'POST',
    headers: {},
    body: form,
  });
}

// ─── Exports ───────────────────────────────────────────────────────────────────
/**
 * GET /api/export/csv
 * Returns CSV data as a string.
 */
export async function exportCSV() {
  if (USE_MOCK) {
    await delay(300);
    const data = getExportData();
    const header = ['id','timestamp','source_ip','target_url','attack_type','severity','confidence','result','detection_method'];
    const rows = data.attacks.map(a =>
      header.map(k => `"${String(a[k] ?? '').replace(/"/g, '""')}"`).join(',')
    );
    return [header.join(','), ...rows].join('\n');
  }
  const res = await fetch(`${BACKEND_URL}/export/csv`);
  return res.text();
}

/**
 * GET /api/export/json
 * Returns full analysis data as JSON.
 */
export async function exportJSON() {
  if (USE_MOCK) {
    await delay(300);
    return getExportData();
  }
  return request('/export/json');
}

// ─── ML Intelligence ───────────────────────────────────────────────────────────
/**
 * GET /api/ml/status
 * Returns ML model availability and metadata.
 */
export async function getMLStatus() {
  if (USE_MOCK) {
    await delay(300);
    return {
      ml_available: true,
      model_type: 'RandomForest',
      n_estimators: 150,
      n_classes: 14,
      n_features: 13,
      confidence_threshold: 0.55,
      classes: [
        'Brute Force','Command Injection','Credential Stuffing',
        'Directory Traversal','HTTP Parameter Pollution','LFI/RFI',
        'Normal','SQL Injection','SSRF','Typosquatting',
        'Web Shell Upload','XSS','XXE','Benign'
      ],
      label: 'Prototype Prediction',
      disclaimer: 'Demo prototype trained on synthetic data only.',
    };
  }
  return request('/ml/status');
}

/**
 * POST /api/ml/predict
 * Run a single HTTP request through the RF classifier.
 */
export async function predictML(requestData) {
  if (USE_MOCK) {
    await delay(400);
    const url = (requestData.url || '').toLowerCase();
    if (url.includes('union') || url.includes('select'))
      return { prediction: 'SQL Injection', confidence: 0.94, label: 'Prototype Prediction', model: 'RandomForest', ml_available: true };
    if (url.includes('<script') || url.includes('onerror'))
      return { prediction: 'XSS', confidence: 0.91, label: 'Prototype Prediction', model: 'RandomForest', ml_available: true };
    if (url.includes('../') || url.includes('passwd'))
      return { prediction: 'Directory Traversal', confidence: 0.88, label: 'Prototype Prediction', model: 'RandomForest', ml_available: true };
    if (url.includes('cmd=') || url.includes('whoami'))
      return { prediction: 'Command Injection', confidence: 0.96, label: 'Prototype Prediction', model: 'RandomForest', ml_available: true };
    return { prediction: 'Normal', confidence: 0.82, label: 'Prototype Prediction', model: 'RandomForest', ml_available: true };
  }
  return request('/ml/predict', {
    method: 'POST',
    body: JSON.stringify(requestData),
  });
}

/**
 * GET /api/ml/metrics
 * Returns evaluation metrics from the last training run.
 */
export async function getMLMetrics() {
  if (USE_MOCK) {
    await delay(350);
    return {
      accuracy: 0.9261,
      precision: 0.9318,
      recall: 0.9261,
      f1: 0.9274,
      n_test_samples: 222,
      train_size: 888,
      test_size: 222,
      model_type: 'RandomForestClassifier',
      n_estimators: 150,
      trained_at: new Date(Date.now() - 3600000).toISOString(),
      classes: [
        'Brute Force','Command Injection','Credential Stuffing',
        'Directory Traversal','HTTP Parameter Pollution','LFI/RFI',
        'Normal','SQL Injection','SSRF','Typosquatting',
        'Web Shell Upload','XSS','XXE'
      ],
      features: [
        'url_length','param_count','special_char_count','encoding_count',
        'path_depth','suspicious_keyword_count','http_method_encoded',
        'status_code','response_size','has_dot_dot','has_base64','is_post','query_length'
      ],
      disclaimer: 'Prototype metrics — evaluated on synthetic data only.',
      note: 'Prototype metrics — synthetic data only',
    };
  }
  return request('/ml/metrics');
}
