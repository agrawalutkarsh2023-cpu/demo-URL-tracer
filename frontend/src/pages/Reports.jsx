import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import {
  FileDown, FileJson, FileText, ShieldAlert, Globe,
  CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Info
} from 'lucide-react';

import { mockDashboard, mockAttacks, mockIPProfiles } from '../mock/mockData.js';
import ExportButton from '../components/common/ExportButton.jsx';
import RiskBadge    from '../components/common/RiskBadge.jsx';
import StatCard     from '../components/common/StatCard.jsx';
import { Activity } from 'lucide-react';

function Section({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="glass-card border border-dark-600/50 overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-dark-700/30 transition-colors"
      >
        <span className="text-sm font-semibold text-white">{title}</span>
        {open ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
      </button>
      {open && <div className="border-t border-dark-700/50">{children}</div>}
    </div>
  );
}

export default function Reports() {
  const successCount = mockAttacks.filter(a => a.result === 'POTENTIAL_SUCCESS').length;
  const critCount    = mockAttacks.filter(a => a.severity === 'CRITICAL').length;
  const ipProfiles   = Object.values(mockIPProfiles);
  const highRiskIPs  = ipProfiles.filter(ip => ['HIGH','CRITICAL'].includes(ip.risk_level));

  return (
    <div className="space-y-5 animate-fade-in">

      {/* Notice */}
      <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2.5">
        <Info className="w-4 h-4 flex-shrink-0" />
        All exported data is <strong>simulated/synthetic</strong>. A disclaimer is embedded in every export.
      </div>

      {/* Export actions */}
      <div className="glass-card border border-dark-600/50 p-5">
        <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <FileDown className="w-4 h-4 text-cyber-500" />
          Export Analysis Data
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* CSV */}
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-4 flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-900/30 border border-green-700/30 flex items-center justify-center flex-shrink-0">
              <FileText className="w-6 h-6 text-green-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white mb-0.5">Attack Log — CSV</p>
              <p className="text-xs text-slate-500 mb-3">
                {mockAttacks.length} records · id, timestamp, source_ip, attack_type, severity, confidence, result, method
              </p>
              <ExportButton type="csv" label="Download CSV" />
            </div>
          </div>

          {/* JSON */}
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-4 flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-900/30 border border-blue-700/30 flex items-center justify-center flex-shrink-0">
              <FileJson className="w-6 h-6 text-blue-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white mb-0.5">Full Analysis — JSON</p>
              <p className="text-xs text-slate-500 mb-3">
                Attacks + IP profiles + dashboard summary + metadata + disclaimer
              </p>
              <ExportButton type="json" label="Download JSON" />
            </div>
          </div>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Attacks"         value={mockAttacks.length}     icon={ShieldAlert}    color="red" />
        <StatCard label="Potential Successes"   value={successCount}           icon={CheckCircle2}   color="purple" />
        <StatCard label="Critical Severity"     value={critCount}              icon={AlertTriangle}  color="orange" />
        <StatCard label="IPs Tracked"           value={ipProfiles.length}      icon={Globe}          color="cyan" />
      </div>

      {/* Collapsible sections */}
      <Section title={`Attack Log Preview (${mockAttacks.length} records)`} defaultOpen>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Source IP</th>
                <th>Attack Type</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {mockAttacks.slice(0, 10).map(atk => (
                <tr key={atk.id}>
                  <td className="text-xs font-mono text-slate-500">{atk.id}</td>
                  <td className="font-mono text-xs text-slate-400 whitespace-nowrap">
                    {format(parseISO(atk.timestamp), 'MM/dd HH:mm')}
                  </td>
                  <td className="font-mono text-xs text-cyber-400 whitespace-nowrap">{atk.source_ip}</td>
                  <td className="text-slate-300 whitespace-nowrap">{atk.attack_type}</td>
                  <td><RiskBadge severity={atk.severity} /></td>
                  <td className="font-mono text-xs text-slate-400">{(atk.confidence * 100).toFixed(0)}%</td>
                  <td>
                    <span className={`text-xs font-mono ${
                      atk.result === 'POTENTIAL_SUCCESS' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {atk.result === 'POTENTIAL_SUCCESS' ? '⚡ SUCCESS' : '⚠ ATTEMPT'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-slate-600 font-mono text-center py-3 border-t border-dark-700/50">
            Showing 10 of {mockAttacks.length} records — download CSV for full dataset
          </p>
        </div>
      </Section>

      <Section title={`IP Risk Profiles (${ipProfiles.length} IPs)`}>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Requests</th>
                <th>Attacks</th>
                <th>Attack Types</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {ipProfiles.map(ip => (
                <tr key={ip.ip}>
                  <td className="font-mono text-xs text-cyber-400">{ip.ip}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="progress-bar w-16">
                        <div
                          className="progress-fill bg-red-500"
                          style={{ width: `${ip.risk_score}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-400">{ip.risk_score}</span>
                    </div>
                  </td>
                  <td><RiskBadge severity={ip.risk_level} /></td>
                  <td className="font-mono text-xs text-slate-400">{ip.total_requests}</td>
                  <td className="font-mono text-xs text-slate-400">{ip.attack_count}</td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {ip.attack_types.slice(0, 2).map(t => (
                        <span key={t} className="text-[10px] bg-dark-700 border border-dark-600 rounded px-1.5 py-0.5 text-slate-400">
                          {t}
                        </span>
                      ))}
                      {ip.attack_types.length > 2 && (
                        <span className="text-[10px] text-slate-600">+{ip.attack_types.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td className="font-mono text-xs text-slate-500 whitespace-nowrap">
                    {format(parseISO(ip.last_seen), 'MM/dd HH:mm')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* JSON preview */}
      <Section title="JSON Export Preview">
        <div className="p-5">
          <pre className="text-xs font-mono text-slate-400 bg-dark-900 rounded-lg p-4 overflow-x-auto leading-relaxed max-h-72">
{`{
  "metadata": {
    "exported_at": "${new Date().toISOString()}",
    "data_type": "SIMULATED_DEMO_DATA",
    "total_attacks": ${mockAttacks.length},
    "disclaimer": "This data is entirely synthetic and generated for demonstration purposes only."
  },
  "attacks": [ ... ${mockAttacks.length} records ... ],
  "ip_profiles": [ ... ${ipProfiles.length} profiles ... ],
  "dashboard_summary": {
    "total_requests": ${mockDashboard.total_requests},
    "total_attacks":  ${mockDashboard.total_attacks},
    "high_risk_ips":  ${mockDashboard.high_risk_ips},
    "potential_successes": ${mockDashboard.potential_successes}
  }
}`}
          </pre>
        </div>
      </Section>
    </div>
  );
}
