import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ShieldAlert, Globe, CheckCircle2, RefreshCw } from 'lucide-react';
import { format, parseISO } from 'date-fns';

import { getDashboard, getAttacks } from '../api/apiService.js';
import StatCard       from '../components/common/StatCard.jsx';
import RiskBadge      from '../components/common/RiskBadge.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import AttackChart    from '../components/charts/AttackChart.jsx';
import SeverityChart  from '../components/charts/SeverityChart.jsx';
import Timeline       from '../components/charts/Timeline.jsx';

export default function Dashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [recent, setRecent]       = useState([]);
  const [loading, setLoading]     = useState(true);

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

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div className="space-y-6 animate-fade-in">

      {/* Top bar */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-500 font-mono">
            Last refresh: {format(new Date(), 'HH:mm:ss')} &nbsp;·&nbsp; <span className="text-amber-400">DEMO DATA</span>
          </p>
        </div>
        <button onClick={loadData} className="btn-secondary text-xs gap-1.5 px-3 py-1.5">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Requests"
          value={dashboard.total_requests}
          icon={Activity}
          color="cyan"
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
          label="High Risk IPs"
          value={dashboard.high_risk_ips}
          icon={Globe}
          color="orange"
          sub="CRITICAL / HIGH risk"
        />
        <StatCard
          label="Potential Successes"
          value={dashboard.potential_successes}
          icon={CheckCircle2}
          color="purple"
          trend={-5}
          sub="Possibly exploited"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Attack distribution */}
        <div className="lg:col-span-2 glass-card p-5 border border-dark-600/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Attack Distribution</h2>
            <span className="text-[10px] font-mono text-slate-500 bg-dark-700 rounded px-2 py-0.5">SIMULATED</span>
          </div>
          <AttackChart data={dashboard.attack_distribution} />
        </div>

        {/* Severity */}
        <div className="glass-card p-5 border border-dark-600/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Severity Distribution</h2>
            <span className="text-[10px] font-mono text-slate-500 bg-dark-700 rounded px-2 py-0.5">SIMULATED</span>
          </div>
          <SeverityChart data={dashboard.severity_distribution} />
        </div>
      </div>

      {/* Timeline */}
      <div className="glass-card p-5 border border-dark-600/50">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">Attack Timeline — Last 7 Days</h2>
          <span className="text-[10px] font-mono text-slate-500 bg-dark-700 rounded px-2 py-0.5">SIMULATED</span>
        </div>
        <Timeline data={dashboard.attack_timeline} />
      </div>

      {/* Recent detections */}
      <div className="glass-card border border-dark-600/50 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-dark-700/50">
          <h2 className="text-sm font-semibold text-white">Recent Detections</h2>
          <button
            onClick={() => navigate('/attacks')}
            className="text-xs text-cyber-400 hover:text-cyber-300 transition-colors"
          >
            View all →
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
              </tr>
            </thead>
            <tbody>
              {recent.map(atk => (
                <tr key={atk.id} onClick={() => navigate('/attacks', { state: { selected: atk.id } })}>
                  <td className="font-mono text-xs text-slate-400">
                    {format(parseISO(atk.timestamp), 'MM/dd HH:mm:ss')}
                  </td>
                  <td className="font-mono text-xs text-cyber-400">{atk.source_ip}</td>
                  <td className="text-slate-300">{atk.attack_type}</td>
                  <td><RiskBadge severity={atk.severity} /></td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="progress-bar w-16">
                        <div
                          className="progress-fill bg-cyber-500"
                          style={{ width: `${atk.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        {(atk.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`text-xs font-mono font-semibold ${
                      atk.result === 'POTENTIAL_SUCCESS' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {atk.result === 'POTENTIAL_SUCCESS' ? '⚡ SUCCESS' : '⚠ ATTEMPT'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
