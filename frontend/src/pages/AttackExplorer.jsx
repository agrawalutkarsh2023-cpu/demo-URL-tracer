import { useState, useEffect, useCallback } from 'react';
import { format, parseISO } from 'date-fns';
import { ChevronLeft, ChevronRight, X, ExternalLink, Activity, Info } from 'lucide-react';

import { getAttacks } from '../api/apiService.js';
import FilterBar      from '../components/common/FilterBar.jsx';
import RiskBadge      from '../components/common/RiskBadge.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import EmptyState     from '../components/common/EmptyState.jsx';
import ExportButton   from '../components/common/ExportButton.jsx';

const PAGE_SIZE = 12;

// Detail modal
function AttackDetail({ attack, onClose }) {
  if (!attack) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-dark-950/80 backdrop-blur-sm" />
      <div
        className="relative glass-card border border-dark-500 w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-fade-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-dark-700/50">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <RiskBadge severity={attack.severity} />
              <span className="text-xs font-mono text-slate-500">{attack.id}</span>
            </div>
            <h2 className="text-lg font-bold text-white">{attack.attack_type}</h2>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-dark-700 rounded-lg transition-colors">
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-5">
          {/* Warning */}
          <div className="flex items-start gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
            This is simulated/synthetic data. Not real intelligence.
          </div>

          {/* Grid fields */}
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'Source IP',        value: attack.source_ip,        mono: true, accent: true },
              { label: 'Timestamp',        value: format(parseISO(attack.timestamp), 'PPpp'), mono: true },
              { label: 'Detection Method', value: attack.detection_method },
              { label: 'Result',           value: attack.result === 'POTENTIAL_SUCCESS' ? '⚡ Potential Success' : '⚠ Attempt',
                cls: attack.result === 'POTENTIAL_SUCCESS' ? 'text-red-400' : 'text-yellow-400' },
              { label: 'Confidence',       value: `${(attack.confidence * 100).toFixed(1)}%`, mono: true },
              { label: 'Severity',         custom: <RiskBadge severity={attack.severity} /> },
            ].map(({ label, value, custom, mono, accent, cls }) => (
              <div key={label} className="bg-dark-800/60 rounded-lg p-3">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                {custom ?? (
                  <p className={`text-sm font-medium ${mono ? 'font-mono' : ''} ${accent ? 'text-cyber-400' : cls ?? 'text-slate-200'}`}>
                    {value}
                  </p>
                )}
              </div>
            ))}
          </div>

          {/* Target URL */}
          <div className="bg-dark-800/60 rounded-lg p-3">
            <p className="text-xs text-slate-500 mb-1.5">Target URL</p>
            <p className="text-xs font-mono text-slate-300 break-all leading-relaxed">{attack.target_url}</p>
          </div>

          {/* Payload */}
          <div className="bg-dark-800/60 rounded-lg p-3">
            <p className="text-xs text-slate-500 mb-1.5">Payload / Indicator</p>
            <p className="text-xs font-mono text-red-400 break-all leading-relaxed">{attack.payload}</p>
          </div>

          {/* Confidence bar */}
          <div className="bg-dark-800/60 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs text-slate-500">ML Confidence Score</p>
              <p className="text-xs font-mono font-bold text-cyber-400">
                {(attack.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div className="progress-bar h-2">
              <div
                className={`progress-fill ${attack.confidence >= 0.9 ? 'bg-red-500' : attack.confidence >= 0.75 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                style={{ width: `${attack.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AttackExplorer() {
  const [attacks, setAttacks]       = useState([]);
  const [loading, setLoading]       = useState(true);
  const [selected, setSelected]     = useState(null);
  const [page, setPage]             = useState(1);
  const [filters, setFilters]       = useState({
    search: '', attack_type: 'ALL', severity: 'ALL', result: 'ALL', source_ip: ''
  });

  const fetchAttacks = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAttacks(filters);
      setAttacks(data);
      setPage(1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetchAttacks(); }, [fetchAttacks]);

  const totalPages = Math.ceil(attacks.length / PAGE_SIZE);
  const paged      = attacks.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyber-500" />
          <span className="text-sm text-slate-400 font-mono">
            {attacks.length} attack{attacks.length !== 1 ? 's' : ''} found
          </span>
        </div>
        <div className="flex items-center gap-2">
          <ExportButton type="csv" />
          <ExportButton type="json" />
        </div>
      </div>

      {/* Filters */}
      <FilterBar filters={filters} onFilter={setFilters} />

      {/* Table */}
      <div className="glass-card border border-dark-600/50 overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Fetching attacks..." />
        ) : attacks.length === 0 ? (
          <EmptyState
            title="No attacks found"
            message="Try adjusting your filters to see results."
            icon="search"
          />
        ) : (
          <>
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
                    <th>Method</th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map(atk => (
                    <tr key={atk.id} onClick={() => setSelected(atk)}>
                      <td className="font-mono text-xs text-slate-400 whitespace-nowrap">
                        {format(parseISO(atk.timestamp), 'MM/dd HH:mm:ss')}
                      </td>
                      <td className="font-mono text-xs text-cyber-400 whitespace-nowrap">{atk.source_ip}</td>
                      <td className="text-slate-200 whitespace-nowrap">{atk.attack_type}</td>
                      <td><RiskBadge severity={atk.severity} /></td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="progress-bar w-14">
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
                      <td className="text-xs text-slate-500">{atk.detection_method}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-dark-700/50">
                <span className="text-xs text-slate-500 font-mono">
                  Page {page} of {totalPages} &nbsp;·&nbsp; {attacks.length} records
                </span>
                <div className="flex items-center gap-1">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage(p => p - 1)}
                    className="btn-secondary px-2 py-1.5 disabled:opacity-40"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                        p === page
                          ? 'bg-cyber-700 text-white'
                          : 'bg-dark-800 text-slate-400 hover:bg-dark-700'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage(p => p + 1)}
                    className="btn-secondary px-2 py-1.5 disabled:opacity-40"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Detail modal */}
      {selected && <AttackDetail attack={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
