import { SearchX, WifiOff, ShieldOff, FileX } from 'lucide-react';

const ICONS = {
  search:  SearchX,
  offline: WifiOff,
  shield:  ShieldOff,
  file:    FileX,
};

/**
 * @param {string} title
 * @param {string} [message]
 * @param {'search'|'offline'|'shield'|'file'} [icon]
 * @param {React.ReactNode} [action]
 */
export default function EmptyState({ title, message, icon = 'search', action }) {
  const Icon = ICONS[icon] ?? ICONS.search;

  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center"
        style={{
          background: 'rgba(3,83,82,0.10)',
          border: '1px solid rgba(3,83,82,0.22)',
        }}
      >
        <Icon className="w-7 h-7" style={{ color: 'var(--text-muted)' }} />
      </div>
      <div>
        <h3 className="text-base font-semibold" style={{ color: 'var(--text-secondary)' }}>{title}</h3>
        {message && (
          <p className="text-sm mt-1 max-w-sm" style={{ color: 'var(--text-muted)' }}>{message}</p>
        )}
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
