import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import {
  Search, Globe, AlertOctagon, ShieldAlert, Clock, Wifi,
  BarChart2, Activity, Hash, Info, ChevronRight
} from 'lucide-react';

import { getIPDetail, getIPs } from '../api/apiService.js';
import { mockIPProfiles } from '../mock/mockData.js';
import RiskBadge      from '../components/common/RiskBadge.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import EmptyState     from '../components/common/EmptyState.jsx';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const RISK_SCORE_COLOR = (s) => {
  if (s >= 85) return 'text-red-500';
  if (s >= 65) return 'text-orange-400';
  if (s >= 40) return 'text-yellow-400';
  return 'text-green-400';
};

const RISK_SCORE_RING = (s) => {
  if (s >= 85) return '#ef4444';
  if (s >= 65) return '#f97316';
  if (s >= 40) return '#eab308';
  return '#22c55e';
};

const KNOWN_IPS = Object.keys(mockIPProfiles);

function RiskGauge({ score }) {
  const color = RISK_SCORE_RING(score);
  const circumference = 2 * Math.PI * 42;
  const progress = ((100 - score) / 100) * circumference;

  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#1a2340" strokeWidth="8" />
        <circle
          cx="50" cy="50" r="42" fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={progress}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="absolute text-center">
        <p className={`text-2xl font-bold ${RISK_SCORE_COLOR(score)}`}>{score}</p>
        <p className="text-[10px] text-slate-500 font-mono">RISK</p>
      </div>
    </div>
  );
}

export default function IPIntelligence() {
  const [query, setQuery]     = useState('');
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const search = async (ip) => {
    const q = (ip ?? query).trim();
    if (!q) return;
    setLoading(true);
    setError('');
    setProfile(null);
    try {
      const data = await getIPDetail(q);
      setProfile(data);
    } catch (err) {
      setError(`No data found for "${q}". Try one of the example IPs below.`);
    } finally {
      setLoading(false);
    }
  };

  const activityMax = profile
    ? Math.max(...(profile.daily_activity ?? []).map(d => d.requests), 1)
    : 1;

  return (
    <div className="space-y-5 animate-fade-in">

      {/* Search */}
      <div className="glass-card border border-dark-600/50 p-5">
        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
          Search Synthetic IP Address
        </label>
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="e.g. 192.168.1.25"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && search()}
              className="cyber-input pl-10 font-mono"
            />
          </div>
          <button onClick={() => search()} className="btn-primary px-6">
            <Search className="w-4 h-4" />
            Analyse
          </button>
        </div>

        {/* Quick IPs */}
        <div className="mt-4">
          <p className="text-[11px] text-slate-600 mb-2 font-mono uppercase tracking-wider">
            Demo IPs (click to load):
          </p>
          <div className="flex flex-wrap gap-2">
            {KNOWN_IPS.map(ip => (
              <button
                key={ip}
                onClick={() => { setQuery(ip); search(ip); }}
                className="px-2.5 py-1 text-xs font-mono rounded-lg bg-dark-700 border border-dark-600
                           text-cyber-400 hover:bg-dark-600 hover:border-cyber-700 transition-colors"
              >
                {ip}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Simulated data notice */}
      <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2.5">
        <Info className="w-4 h-4 flex-shrink-0" />
        All IP data shown here is <strong>100% simulated</strong>. These are fictional private IP addresses, not real threat intelligence.
      </div>

      {/* Loading */}
      {loading && <LoadingSpinner message="Analysing IP..." />}

      {/* Error */}
      {error && !loading && (
        <EmptyState title="IP Not Found" message={error} icon="search" />
      )}

      {/* Profile */}
      {profile && !loading && (
        <div className="space-y-4 animate-fade-in">
          {/* IP Header Card */}
          <div className="glass-card border border-dark-600/50 p-5">
            <div className="flex flex-wrap items-center gap-6">
              {/* Gauge */}
              <RiskGauge score={profile.risk_score} />

              {/* Info */}
              <div className="flex-1 min-w-60">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl font-bold font-mono text-white">{profile.ip}</span>
                  <RiskBadge severity={profile.risk_level === 'CRITICAL' ? 'CRITICAL' : profile.risk_level} />
                  <span className="text-[10px] font-mono text-slate-600 bg-dark-700 rounded px-2 py-0.5">SIMULATED</span>
                </div>
                <p className="text-xs text-slate-500 font-mono mb-4">{profile.hostname}</p>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: 'Total Requests', value: profile.total_requests, icon: Activity },
                    { label: 'Attacks',         value: profile.attack_count,   icon: ShieldAlert },
                    { label: 'First Seen',
                      value: format(parseISO(profile.first_seen), 'MMM d'), icon: Clock },
                    { label: 'Last Seen',
                      value: format(parseISO(profile.last_seen), 'MMM d HH:mm'), icon: Clock },
                  ].map(({ label, value, icon: Icon }) => (
                    <div key={label} className="bg-dark-800/60 rounded-lg p-3">
                      <div className="flex items-center gap-1.5 mb-1">
                        <Icon className="w-3.5 h-3.5 text-slate-500" />
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">{label}</p>
                      </div>
                      <p className="text-sm font-bold text-white font-mono">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Attack types + Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Attack types breakdown */}
            <div className="glass-card border border-dark-600/50 p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Hash className="w-4 h-4 text-cyber-500" />
                Attack Types
              </h3>
              <div className="space-y-3">
                {profile.attack_types.map((type, i) => {
                  const attacks = (profile.attacks ?? []).filter(a => a.attack_type === type);
                  const pct = profile.attack_count > 0
                    ? Math.round((attacks.length / profile.attack_count) * 100)
                    : Math.round(100 / profile.attack_types.length);
                  return (
                    <div key={type}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-slate-300">{type}</span>
                        <span className="text-xs font-mono text-slate-500">{attacks.length > 0 ? attacks.length : '—'}</span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${pct}%`,
                            background: ['#ef4444','#f97316','#eab308','#22c55e','#3b82f6','#8b5cf6','#06b6d4','#ec4899'][i % 8]
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Daily activity mini-chart */}
            <div className="glass-card border border-dark-600/50 p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-cyber-500" />
                Daily Activity
              </h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart
                  data={profile.daily_activity}
                  margin={{ top: 4, right: 4, left: -20, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a2340" vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: '#141c34', border: '1px solid #2d3a5c', borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Bar dataKey="requests" name="Requests" fill="#00997a" radius={[3,3,0,0]} />
                  <Bar dataKey="attacks"  name="Attacks"  fill="#ef4444" radius={[3,3,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Attacks from this IP */}
          {profile.attacks?.length > 0 && (
            <div className="glass-card border border-dark-600/50 overflow-hidden">
              <div className="px-5 py-4 border-b border-dark-700/50">
                <h3 className="text-sm font-semibold text-white">
                  Attacks from {profile.ip}
                  <span className="ml-2 text-xs text-slate-500 font-mono">({profile.attacks.length})</span>
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Attack Type</th>
                      <th>Severity</th>
                      <th>Result</th>
                      <th>Method</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profile.attacks.slice(0, 10).map(atk => (
                      <tr key={atk.id}>
                        <td className="font-mono text-xs text-slate-400 whitespace-nowrap">
                          {format(parseISO(atk.timestamp), 'MM/dd HH:mm')}
                        </td>
                        <td className="text-slate-300">{atk.attack_type}</td>
                        <td><RiskBadge severity={atk.severity} /></td>
                        <td>
                          <span className={`text-xs font-mono ${
                            atk.result === 'POTENTIAL_SUCCESS' ? 'text-red-400' : 'text-yellow-400'
                          }`}>
                            {atk.result === 'POTENTIAL_SUCCESS' ? '⚡ SUCCESS' : '⚠ ATTEMPT'}
                          </span>
                        </td>
                        <td className="text-xs text-slate-500">{atk.detection_method}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Initial state */}
      {!profile && !loading && !error && (
        <EmptyState
          title="Enter an IP address"
          message="Type a synthetic IP above or click one of the demo IPs to see a full risk profile."
          icon="search"
        />
      )}
    </div>
  );
}
