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
      <div className="w-16 h-16 rounded-2xl bg-dark-800 border border-dark-600 flex items-center justify-center">
        <Icon className="w-7 h-7 text-slate-600" />
      </div>
      <div>
        <h3 className="text-base font-semibold text-slate-400">{title}</h3>
        {message && <p className="text-sm text-slate-600 mt-1 max-w-sm">{message}</p>}
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
