import { useLocation } from 'react-router-dom';
import { AlertTriangle, Bell, Clock } from 'lucide-react';
import { format } from 'date-fns';

const PAGE_TITLES = {
  '/':                { title: 'Dashboard',       subtitle: 'System overview & recent detections' },
  '/attacks':         { title: 'Attack Explorer', subtitle: 'Browse, filter, and inspect detected attacks' },
  '/ip-intelligence': { title: 'IP Intelligence', subtitle: 'Search and analyse simulated IP risk profiles' },
  '/pcap':            { title: 'PCAP Analysis',   subtitle: 'Upload and process packet capture files' },
  '/reports':         { title: 'Reports',         subtitle: 'Export analysis data as CSV or JSON' },
};

export default function Header() {
  const { pathname } = useLocation();
  const info = PAGE_TITLES[pathname] ?? { title: 'URL-Tracer', subtitle: 'Demo Prototype' };

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between px-6 py-3.5
                        bg-dark-950/80 backdrop-blur-md border-b border-dark-700/50">
      {/* Page identity */}
      <div>
        <h1 className="text-lg font-bold text-white">{info.title}</h1>
        <p className="text-xs text-slate-500">{info.subtitle}</p>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Demo banner */}
        <div className="demo-banner">
          <AlertTriangle className="w-3.5 h-3.5" />
          DEMO / SIMULATED DATA
        </div>

        {/* Clock */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500 font-mono
                        bg-dark-800 border border-dark-600 rounded-lg px-3 py-1.5">
          <Clock className="w-3.5 h-3.5" />
          {format(new Date(), 'dd MMM yyyy HH:mm')}
        </div>

        {/* Notification bell (decorative for demo) */}
        <button className="relative w-9 h-9 rounded-lg bg-dark-800 border border-dark-600
                           flex items-center justify-center hover:bg-dark-700 transition-colors">
          <Bell className="w-4 h-4 text-slate-400" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500" />
        </button>
      </div>
    </header>
  );
}
