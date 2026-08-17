import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ShieldAlert,
  Globe,
  FileSearch,
  FileBarChart2,
  Shield,
  Wifi,
  AlertTriangle,
} from 'lucide-react';

const navItems = [
  { to: '/',                label: 'Dashboard',       icon: LayoutDashboard },
  { to: '/attacks',         label: 'Attack Explorer', icon: ShieldAlert },
  { to: '/ip-intelligence', label: 'IP Intelligence', icon: Globe },
  { to: '/pcap',            label: 'PCAP Analysis',   icon: FileSearch },
  { to: '/reports',         label: 'Reports',         icon: FileBarChart2 },
];

export default function Sidebar() {
  return (
    <aside className="flex flex-col w-64 min-h-screen bg-dark-900 border-r border-dark-700/60 flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-dark-700/60">
        <div className="relative">
          <div className="w-9 h-9 rounded-lg bg-cyber-600/20 border border-cyber-500/40 flex items-center justify-center glow-cyan">
            <Shield className="w-5 h-5 text-cyber-400" />
          </div>
          {/* Pulse dot */}
          <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-cyber-400 animate-pulse-slow" />
        </div>
        <div>
          <span className="text-base font-bold text-white tracking-tight"><URL-Tracer></URL-Tracer></span>
          <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">Detection System</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="px-3 mb-2 text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
          Navigation
        </p>
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Demo notice */}
      <div className="px-4 py-4 border-t border-dark-700/60">
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
          <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-semibold text-amber-400">Demo Mode</p>
            <p className="text-[10px] text-slate-500 mt-0.5 leading-relaxed">
              All data is synthetic &amp; simulated. Not real intelligence.
            </p>
          </div>
        </div>

        {/* Status */}
        <div className="mt-3 flex items-center gap-2">
          <Wifi className="w-3.5 h-3.5 text-cyber-500" />
          <span className="text-[10px] font-mono text-cyber-600">DEMO-ENV ACTIVE</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyber-500 animate-pulse ml-auto" />
        </div>
      </div>
    </aside>
  );
}
