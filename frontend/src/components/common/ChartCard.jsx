/**
 * ChartCard — reusable wrapper for all chart panels.
 * Eliminates the repeated glass-card + section-header boilerplate.
 *
 * @param {string}            title
 * @param {React.ElementType} [icon]
 * @param {string}            [badge]       - small chip label e.g. "SIMULATED"
 * @param {React.ReactNode}   [action]      - right-side action element
 * @param {string}            [className]   - extra classes on the outer card
 * @param {React.ReactNode}   children
 */
export default function ChartCard({ title, icon: Icon, badge, action, className = '', children }) {
  return (
    <div className={`glass-card p-5 flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <h2
          className="text-sm font-semibold flex items-center gap-2"
          style={{ color: '#F3E8BC' }}
        >
          {Icon && <Icon className="w-4 h-4" style={{ color: '#F3E8BC' }} />}
          {title}
          {badge && (
            <span
              className="text-[10px] font-mono px-1.5 py-0.5 rounded"
              style={{
                background: 'rgba(243,232,188,0.08)',
                border: '1px solid rgba(243,232,188,0.15)',
                color: 'var(--text-muted)',
                letterSpacing: '0.06em',
              }}
            >
              {badge}
            </span>
          )}
        </h2>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0">
        {children}
      </div>
    </div>
  );
}
