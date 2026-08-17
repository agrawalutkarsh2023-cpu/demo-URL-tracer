import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Activity, ShieldAlert, Globe, CheckCircle2, RefreshCw,
  FileSearch, Brain, ArrowRight, Zap, Shield, Clock,
  TrendingUp, AlertTriangle, ChevronRight, Target, BarChart2
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import usePageMeta from '../hooks/usePageMeta.js';

import { getDashboard, getAttacks } from '../api/apiService.js';
import StatCard       from '../components/common/StatCard.jsx';
import RiskBadge      from '../components/common/RiskBadge.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import AttackChart    from '../components/charts/AttackChart.jsx';
import SeverityChart  from '../components/charts/SeverityChart.jsx';
import Timeline       from '../components/charts/Timeline.jsx';

// ── Simulated live activity stream ──────────────────────────
const STREAM_EVENTS = [
  { type: 'SQL Injection',  ip: '192.168.1.25', time: '03:42:18', sev: 'CRITICAL' },
  { type: 'XSS Attack',     ip: '10.0.0.14',    time: '03:41:52', sev: 'HIGH' },
  { type: 'Dir Traversal',  ip: '172.16.0.8',   time: '03:41:05', sev: 'MEDIUM' },
  { type: 'PCAP Analyzed',  ip: '—',            time: '03:40:31', sev: 'LOW' },
  { type: 'Brute Force',    ip: '192.168.0.55',  time: '03:39:47', sev: 'HIGH' },
];

const SEV_DOT = { CRITICAL: '#f87171', HIGH: '#fb923c', MEDIUM: '#fbbf24', LOW: '#4ade80' };

// ── Threat Detail Drawer ────────────────────────────────────
function ThreatDrawer({ attack, onClose }) {
  if (!attack) return null;

  const riskColor =
    attack.severity === 'CRITICAL' ? '#f87171' :
    attack.severity === 'HIGH'     ? '#fb923c' :
    attack.severity === 'MEDIUM'   ? '#fbbf24' : '#4ade80';

  const circumference = 2 * Math.PI * 40;
  const confidence = attack.confidence ?? 0.9;
  const offset = circumference * (1 - confidence);

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50"
        style={{ background: 'rgba(2,8,8,0.7)', backdropFilter: 'blur(4px)' }}
        onClick={onClose}
      />
      {/* Drawer */}
      <aside className="drawer z-50">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5" style={{ borderBottom: '1px solid rgba(3,83,82,0.2)' }}>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <RiskBadge severity={attack.severity} />
              <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>{attack.id}</span>
            </div>
            <h2 className="text-lg font-bold" style={{ color: '#F3E8BC' }}>Threat Analysis</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style={{ background: 'rgba(3,83,82,0.12)', border: '1px solid rgba(3,83,82,0.25)' }}
          >
            ✕
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Attack type header */}
          <div className="text-center py-4">
            <div className="relative w-24 h-24 mx-auto mb-3">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(3,83,82,0.15)" strokeWidth="6"/>
                <circle
                  cx="50" cy="50" r="40" fill="none"
                  stroke={riskColor} strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  style={{ transition: 'stroke-dashoffset 1s ease' }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold num-display" style={{ color: riskColor }}>
                  {Math.round(confidence * 100)}
                </span>
                <span className="text-[9px]" style={{ color: 'var(--text-muted)' }}>CONFIDENCE</span>
              </div>
            </div>
            <h3 className="text-xl font-bold" style={{ color: '#F3E8BC' }}>{attack.attack_type}</h3>
            <p className="text-sm mt-1" style={{ color: riskColor }}>● {attack.severity} SEVERITY</p>
          </div>

          {/* Fields grid */}
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Source IP',   value: attack.source_ip,  accent: true },
              { label: 'Timestamp',   value: format(parseISO(attack.timestamp), 'MM/dd HH:mm:ss'), mono: true },
              { label: 'Method',      value: attack.detection_method },
              { label: 'Result',      value: attack.result === 'POTENTIAL_SUCCESS' ? '⚡ Potential Success' : '⚠ Attempt',
                color: attack.result === 'POTENTIAL_SUCCESS' ? '#f87171' : '#fbbf24' },
            ].map(({ label, value, mono, accent, color }) => (
              <div
                key={label}
                className="rounded-xl p-3"
                style={{ background: 'rgba(3,83,82,0.08)', border: '1px solid rgba(3,83,82,0.15)' }}
              >
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
                <p className={`text-sm font-medium ${mono ? 'font-mono' : ''}`}
                   style={{ color: accent ? '#F3E8BC' : color ?? 'var(--text-primary)' }}>
                  {value}
                </p>
              </div>
            ))}
          </div>

          {/* Target URL */}
          <div className="rounded-xl p-3" style={{ background: 'rgba(3,83,82,0.08)', border: '1px solid rgba(3,83,82,0.15)' }}>
            <p className="text-[10px] uppercase tracking-wider mb-1.5" style={{ color: 'var(--text-muted)' }}>Target URL</p>
            <p className="text-xs font-mono break-all leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {attack.target_url}
            </p>
          </div>

          {/* Payload */}
          <div className="rounded-xl p-3" style={{ background: 'rgba(180,30,30,0.08)', border: '1px solid rgba(180,30,30,0.20)' }}>
            <p className="text-[10px] uppercase tracking-wider mb-1.5" style={{ color: 'var(--text-muted)' }}>Payload / Indicator</p>
            <p className="text-xs font-mono break-all leading-relaxed" style={{ color: '#f87171' }}>
              {attack.payload}
            </p>
          </div>

          {/* Detected indicators */}
          <div className="rounded-xl p-4" style={{ background: 'rgba(3,83,82,0.08)', border: '1px solid rgba(3,83,82,0.18)' }}>
            <p className="text-xs font-semibold mb-3" style={{ color: '#F3E8BC' }}>Detected Indicators</p>
            <div className="space-y-2">
              {['Suspicious query parameter', 'Known attack pattern match', 'Abnormal URL structure'].map(ind => (
                <div key={ind} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: '#f87171' }} />
                  <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{ind}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Simulated data notice */}
          <div className="flex items-start gap-2 rounded-lg px-3 py-2.5 text-xs"
               style={{ background: 'rgba(243,232,188,0.05)', border: '1px solid rgba(243,232,188,0.12)' }}>
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: '#F3E8BC' }} />
            <span style={{ color: 'var(--text-muted)' }}>Simulated / synthetic data. Not real intelligence.</span>
          </div>
        </div>

        {/* Footer action */}
        <div className="px-6 py-4 flex-shrink-0" style={{ borderTop: '1px solid rgba(3,83,82,0.2)' }}>
          <button className="btn-primary w-full justify-center">
            <Shield className="w-4 h-4" />
            Block IP Address
          </button>
        </div>
      </aside>
    </>
  );
}

// ── Main Dashboard ──────────────────────────────────────────
export default function Dashboard() {
  usePageMeta('Dashboard', 'NetTrace Security — Real-time URL threat intelligence and attack detection dashboard.');
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [recent, setRecent]       = useState([]);
  const [loading, setLoading]     = useState(true);
  const [selected, setSelected]   = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dash, attacks] = await Promise.all([getDashboard(), getAttacks()]);
      setDashboard(dash);
      setRecent(attacks.slice(0, 10));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  if (loading) return <LoadingSpinner message="Loading NetTrace dashboard..." />;

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ── Hero CTA Strip ────────────────────────────── */}
      <div className="cta-strip">
        <div className="cta-strip-inner">
          <div className="cta-strip-text">
            {/* Live indicator */}
            <div className="flex items-center gap-2 mb-2">
              <span className="live-dot" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest" style={{ color: '#4ade80' }}>
                Live Threat Monitoring
              </span>
            </div>
            <h2 className="text-lg md:text-xl font-bold leading-tight" style={{ color: '#F3E8BC' }}>
              NetTrace Security
            </h2>
            <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
              Real-time URL threat intelligence and attack detection platform.
            </p>
          </div>
          <div className="cta-strip-actions">
            <Link to="/attacks" id="cta-attacks" className="cta-btn cta-btn-primary">
              <ShieldAlert className="w-4 h-4" />
              Explore Attacks
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link to="/ip-intelligence" id="cta-ip" className="cta-btn cta-btn-secondary">
              <Globe className="w-4 h-4" />
              Analyse IP
            </Link>
            <Link to="/pcap" id="cta-pcap" className="cta-btn cta-btn-secondary">
              <FileSearch className="w-4 h-4" />
              Upload PCAP
            </Link>
          </div>
        </div>
      </div>

      {/* ── Top bar: refresh + timestamp ─────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5" style={{ color: 'var(--text-muted)' }} />
          <p className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            Last refresh: {format(new Date(), 'HH:mm:ss')}
            &nbsp;·&nbsp;
            <span style={{ color: '#F3E8BC' }}>DEMO DATA</span>
          </p>
        </div>
        <button onClick={loadData} className="btn-secondary text-xs gap-1.5 px-3 py-1.5">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* ── Stat Cards ────────────────────────────────── */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Requests"
          value={dashboard.total_requests}
          icon={Activity}
          color="teal"
          trend={12}
          sub="Last 7 days"
        />
        <StatCard
          label="Total Attacks"
          value={dashboard.total_attacks}
          icon={ShieldAlert}
          color="red"
          trend={8}
          sub="Detected & simulated"
        />
        <StatCard
          label="High-Risk IPs"
          value={dashboard.high_risk_ips}
          icon={Globe}
          color="orange"
          sub="CRITICAL / HIGH risk"
        />
        <StatCard
          label="Potential Successes"
          value={dashboard.potential_successes}
          icon={Target}
          color="purple"
          trend={-5}
          sub="Possibly exploited"
        />
      </div>

      {/* ── Charts row ────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Attack distribution */}
        <div className="lg:col-span-2 glass-card p-5">
          <div className="section-header" style={{ padding: '0 0 16px 0', marginBottom: 12 }}>
            <h2 className="section-title flex items-center gap-2">
              <BarChart2 className="w-4 h-4" style={{ color: '#F3E8BC' }} />
              Attack Distribution
            </h2>
            <span className="chip">SIMULATED</span>
          </div>
          <AttackChart data={dashboard.attack_distribution} />
        </div>

        {/* Severity donut */}
        <div className="glass-card p-5">
          <div className="section-header" style={{ padding: '0 0 16px 0', marginBottom: 12 }}>
            <h2 className="section-title flex items-center gap-2">
              <Target className="w-4 h-4" style={{ color: '#F3E8BC' }} />
              Severity
            </h2>
            <span className="chip">SIMULATED</span>
          </div>
          <SeverityChart data={dashboard.severity_distribution} />
        </div>
      </div>

      {/* ── Timeline + Activity Stream ─────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        {/* Timeline chart */}
        <div className="xl:col-span-2 glass-card p-5">
          <div className="section-header" style={{ padding: '0 0 16px 0', marginBottom: 12 }}>
            <h2 className="section-title flex items-center gap-2">
              <Activity className="w-4 h-4" style={{ color: '#F3E8BC' }} />
              Attack Timeline — Last 7 Days
            </h2>
            <span className="chip">SIMULATED</span>
          </div>
          <Timeline data={dashboard.attack_timeline} />
        </div>

        {/* Live Activity Stream */}
        <div className="glass-card p-5">
          <div className="section-header" style={{ padding: '0 0 16px 0', marginBottom: 12 }}>
            <div className="flex items-center gap-2">
              <span className="live-dot" />
              <h2 className="section-title">Activity Stream</h2>
            </div>
            <span className="chip">LIVE</span>
          </div>
          <div className="space-y-0">
            {STREAM_EVENTS.map((ev, i) => (
              <div
                key={i}
                className="stream-item"
                style={{ animationDelay: `${i * 0.08}s` }}
              >
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ background: SEV_DOT[ev.sev] }}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate" style={{ color: 'var(--text-primary)' }}>{ev.type}</p>
                  {ev.ip !== '—' && (
                    <p className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{ev.ip}</p>
                  )}
                </div>
                <span className="text-[10px] font-mono flex-shrink-0" style={{ color: 'var(--text-muted)' }}>{ev.time}</span>
              </div>
            ))}
          </div>

          {/* Security score */}
          <div
            className="mt-4 rounded-xl p-3 text-center"
            style={{ background: 'rgba(3,83,82,0.12)', border: '1px solid rgba(3,83,82,0.22)' }}
          >
            <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>
              System Security Score
            </p>
            <p className="text-2xl font-bold num-display" style={{ color: '#F3E8BC' }}>94%</p>
            <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>All systems operational</p>
          </div>
        </div>
      </div>

      {/* ── Recent Threats Table ─────────────────────── */}
      <div className="glass-card overflow-hidden">
        <div className="section-header">
          <h2 className="section-title flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" style={{ color: '#F3E8BC' }} />
            Recent Threat Detections
          </h2>
          <button
            onClick={() => navigate('/attacks')}
            className="text-xs flex items-center gap-1 transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={e => e.currentTarget.style.color = '#F3E8BC'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            View all <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Source IP</th>
                <th>Attack Type</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Result</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recent.map(atk => (
                <tr
                  key={atk.id}
                  onClick={() => setSelected(atk)}
                  className={selected?.id === atk.id ? 'selected' : ''}
                >
                  <td className="font-mono text-xs whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                    {format(parseISO(atk.timestamp), 'MM/dd HH:mm:ss')}
                  </td>
                  <td className="font-mono text-xs whitespace-nowrap" style={{ color: '#F3E8BC' }}>
                    {atk.source_ip}
                  </td>
                  <td style={{ color: 'var(--text-primary)' }}>{atk.attack_type}</td>
                  <td><RiskBadge severity={atk.severity} /></td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="progress-bar w-16">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${atk.confidence * 100}%`,
                            background: '#035352',
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                        {(atk.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className="text-xs font-mono font-semibold"
                          style={{ color: atk.result === 'POTENTIAL_SUCCESS' ? '#f87171' : '#fbbf24' }}>
                      {atk.result === 'POTENTIAL_SUCCESS' ? '⚡ SUCCESS' : '⚠ ATTEMPT'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="text-xs px-2.5 py-1 rounded-lg transition-all"
                      style={{
                        background: 'rgba(3,83,82,0.12)',
                        border: '1px solid rgba(3,83,82,0.25)',
                        color: '#F3E8BC',
                      }}
                      onClick={e => { e.stopPropagation(); setSelected(atk); }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Threat Detail Drawer */}
      {selected && <ThreatDrawer attack={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
