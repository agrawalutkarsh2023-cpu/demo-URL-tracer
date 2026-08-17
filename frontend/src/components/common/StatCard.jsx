import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const SCHEME = {
  teal:   { grad: 'stat-gradient-teal',   icon: 'rgba(3,83,82,0.5)',    iconText: '#F3E8BC' },
  cyan:   { grad: 'stat-gradient-teal',   icon: 'rgba(3,83,82,0.5)',    iconText: '#F3E8BC' },
  red:    { grad: 'stat-gradient-red',    icon: 'rgba(180,30,30,0.3)',  iconText: '#f87171' },
  orange: { grad: 'stat-gradient-orange', icon: 'rgba(180,90,15,0.3)', iconText: '#fb923c' },
  blue:   { grad: 'stat-gradient-blue',   icon: 'rgba(30,80,180,0.25)', iconText: '#60a5fa' },
  purple: { grad: 'stat-gradient-purple', icon: 'rgba(120,40,180,0.25)', iconText: '#c084fc' },
  cream:  { grad: 'stat-gradient-cream',  icon: 'rgba(243,232,188,0.15)', iconText: '#F3E8BC' },
};

/**
 * @param {string}            label
 * @param {string|number}     value
 * @param {React.ElementType} icon
 * @param {string}            [color]
 * @param {number}            [trend]  - positive = up (bad for attacks, good for others)
 * @param {string}            [sub]
 */
export default function StatCard({ label, value, icon: Icon, color = 'teal', trend, sub }) {
  const s = SCHEME[color] ?? SCHEME.teal;

  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendCls  = trend > 0 ? '#f87171' : trend < 0 ? '#4ade80' : 'var(--text-muted)';

  return (
    <div
      className={`glass-card-hover border ${s.grad} p-5`}
      style={{ transition: 'all 0.2s' }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold uppercase tracking-widest mb-2 truncate"
             style={{ color: 'var(--text-muted)' }}>
            {label}
          </p>
          <p className="text-3xl font-bold leading-none num-display" style={{ color: 'var(--text-primary)' }}>
            {typeof value === 'number' ? value.toLocaleString() : (value ?? '—')}
          </p>
          {sub && (
            <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>
          )}
          {trend !== undefined && (
            <div className="flex items-center gap-1 mt-2 text-xs font-medium" style={{ color: trendCls }}>
              <TrendIcon className="w-3.5 h-3.5" />
              <span>{Math.abs(trend)}% vs yesterday</span>
            </div>
          )}
        </div>

        {/* Icon bubble */}
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: s.icon, border: `1px solid ${s.icon}` }}
        >
          <Icon className="w-5 h-5" style={{ color: s.iconText }} />
        </div>
      </div>
    </div>
  );
}
