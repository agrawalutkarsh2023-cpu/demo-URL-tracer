import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const GRADIENT_MAP = {
  cyan:   'stat-gradient-cyan   border-cyber-700/30',
  red:    'stat-gradient-red    border-red-700/30',
  orange: 'stat-gradient-orange border-orange-700/30',
  blue:   'stat-gradient-blue   border-blue-700/30',
  purple: 'stat-gradient-purple border-purple-700/30',
};

const ICON_COLOR_MAP = {
  cyan:   'text-cyber-400   bg-cyber-900/50',
  red:    'text-red-400     bg-red-900/30',
  orange: 'text-orange-400  bg-orange-900/30',
  blue:   'text-blue-400    bg-blue-900/30',
  purple: 'text-purple-400  bg-purple-900/30',
};

/**
 * @param {string}   label
 * @param {string|number} value
 * @param {React.ElementType} icon
 * @param {'cyan'|'red'|'orange'|'blue'|'purple'} color
 * @param {number}   [trend]   - percentage change, positive or negative
 * @param {string}   [sub]     - subtitle / secondary label
 */
export default function StatCard({ label, value, icon: Icon, color = 'cyan', trend, sub }) {
  const gradient = GRADIENT_MAP[color] ?? GRADIENT_MAP.cyan;
  const iconCls  = ICON_COLOR_MAP[color] ?? ICON_COLOR_MAP.cyan;

  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendCls  = trend > 0 ? 'text-red-400' : trend < 0 ? 'text-green-400' : 'text-slate-500';

  return (
    <div className={`glass-card border ${gradient} p-5 hover:scale-[1.01] transition-transform duration-200`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-1 truncate">
            {label}
          </p>
          <p className="text-3xl font-bold text-white leading-none">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {sub && (
            <p className="text-xs text-slate-500 mt-1.5">{sub}</p>
          )}
          {trend !== undefined && (
            <div className={`flex items-center gap-1 mt-2 text-xs font-medium ${trendCls}`}>
              <TrendIcon className="w-3.5 h-3.5" />
              <span>{Math.abs(trend)}% vs yesterday</span>
            </div>
          )}
        </div>
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${iconCls}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}
