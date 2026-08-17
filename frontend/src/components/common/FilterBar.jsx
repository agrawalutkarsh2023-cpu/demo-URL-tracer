import { Search, Filter, X } from 'lucide-react';
import { ATTACK_TYPES, SEVERITIES } from '../../mock/mockData.js';

const RESULTS = ['ALL', 'ATTEMPT', 'POTENTIAL_SUCCESS'];

const selectStyle = {
  background: 'rgba(3,83,82,0.06)',
  border: '1px solid rgba(3,83,82,0.22)',
  borderRadius: 10,
  padding: '10px 14px',
  color: 'var(--text-primary)',
  fontSize: 13,
  outline: 'none',
  appearance: 'none',
  width: '100%',
  cursor: 'pointer',
};

/**
 * @param {Object}   filters
 * @param {Function} onFilter - called with updated filter object
 */
export default function FilterBar({ filters, onFilter }) {
  const set   = (key, value) => onFilter({ ...filters, [key]: value });
  const reset = () =>
    onFilter({ search: '', attack_type: 'ALL', severity: 'ALL', result: 'ALL', source_ip: '' });

  const hasActive =
    filters.search || filters.attack_type !== 'ALL' ||
    filters.severity !== 'ALL' || filters.result !== 'ALL' || filters.source_ip;

  return (
    <div className="glass-card p-4">
      <div className="flex flex-wrap gap-3 items-end">

        {/* Search */}
        <div className="flex-1 min-w-52">
          <label className="block text-xs mb-1.5 font-semibold uppercase tracking-wider"
                 style={{ color: 'var(--text-muted)' }}>
            Search
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
                    style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Attack type, IP, URL..."
              value={filters.search ?? ''}
              onChange={e => set('search', e.target.value)}
              className="cyber-input pl-9"
            />
          </div>
        </div>

        {/* Source IP */}
        <div className="min-w-40">
          <label className="block text-xs mb-1.5 font-semibold uppercase tracking-wider"
                 style={{ color: 'var(--text-muted)' }}>
            Source IP
          </label>
          <input
            type="text"
            placeholder="e.g. 192.168.1"
            value={filters.source_ip ?? ''}
            onChange={e => set('source_ip', e.target.value)}
            className="cyber-input"
          />
        </div>

        {/* Attack Type */}
        <div className="min-w-44">
          <label className="block text-xs mb-1.5 font-semibold uppercase tracking-wider"
                 style={{ color: 'var(--text-muted)' }}>
            Attack Type
          </label>
          <div className="relative">
            <select
              value={filters.attack_type ?? 'ALL'}
              onChange={e => set('attack_type', e.target.value)}
              style={selectStyle}
            >
              <option value="ALL" style={{ background: '#030e0e' }}>All Types</option>
              {ATTACK_TYPES.map(t => (
                <option key={t} value={t} style={{ background: '#030e0e' }}>{t}</option>
              ))}
            </select>
            <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none"
                    style={{ color: 'var(--text-muted)' }} />
          </div>
        </div>

        {/* Severity */}
        <div className="min-w-36">
          <label className="block text-xs mb-1.5 font-semibold uppercase tracking-wider"
                 style={{ color: 'var(--text-muted)' }}>
            Severity
          </label>
          <select
            value={filters.severity ?? 'ALL'}
            onChange={e => set('severity', e.target.value)}
            style={selectStyle}
          >
            <option value="ALL" style={{ background: '#030e0e' }}>All Levels</option>
            {SEVERITIES.map(s => (
              <option key={s} value={s} style={{ background: '#030e0e' }}>{s}</option>
            ))}
          </select>
        </div>

        {/* Result */}
        <div className="min-w-44">
          <label className="block text-xs mb-1.5 font-semibold uppercase tracking-wider"
                 style={{ color: 'var(--text-muted)' }}>
            Result
          </label>
          <select
            value={filters.result ?? 'ALL'}
            onChange={e => set('result', e.target.value)}
            style={selectStyle}
          >
            {RESULTS.map(r => (
              <option key={r} value={r} style={{ background: '#030e0e' }}>
                {r === 'ALL' ? 'All Results' : r === 'ATTEMPT' ? 'Attempt' : 'Potential Success'}
              </option>
            ))}
          </select>
        </div>

        {/* Reset */}
        {hasActive && (
          <button onClick={reset} className="btn-secondary self-end gap-1.5">
            <X className="w-4 h-4" />
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
