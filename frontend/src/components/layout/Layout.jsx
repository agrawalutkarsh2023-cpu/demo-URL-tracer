import { useState, useEffect } from 'react';
import { Outlet, useLocation, NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Globe, FileSearch, Brain, FileBarChart2, X } from 'lucide-react';
import Sidebar     from './Sidebar.jsx';
import Header      from './Header.jsx';
import Breadcrumbs from '../common/Breadcrumbs.jsx';

// ── Mobile bottom nav items ──────────────────────────────
const MOBILE_NAV = [
  { to: '/',                label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/attacks',         label: 'Attacks',   icon: ShieldAlert },
  { to: '/ip-intelligence', label: 'IP Intel',  icon: Globe },
  { to: '/pcap',            label: 'PCAP',      icon: FileSearch },
  { to: '/ml',              label: 'ML',        icon: Brain },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Close mobile sidebar on route change
  useEffect(() => { setSidebarOpen(false); }, [location.pathname]);

  // Lock body scroll when sidebar drawer is open on mobile
  useEffect(() => {
    document.body.style.overflow = sidebarOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [sidebarOpen]);

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-base)', position: 'relative', zIndex: 1 }}>

      {/* ── Desktop sidebar ──────────────────────────── */}
      <div className="hidden md:flex">
        <Sidebar />
      </div>

      {/* ── Mobile sidebar overlay ───────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ background: 'rgba(2,8,8,0.75)', backdropFilter: 'blur(4px)' }}
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── Mobile sidebar drawer ────────────────────── */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-in-out md:hidden
                    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="relative h-full">
          <Sidebar />
          <button
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
            className="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style={{ background: 'rgba(3,83,82,0.15)', border: '1px solid rgba(3,83,82,0.3)' }}
          >
            <X className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>
      </div>

      {/* ── Main content column ──────────────────────── */}
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <Breadcrumbs />

        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 animate-fade-in" style={{ position: 'relative', zIndex: 1 }}>
          <Outlet />
        </main>

        {/* ── Sticky mobile bottom nav ─────────────── */}
        <nav
          aria-label="Mobile navigation"
          className="fixed bottom-0 left-0 right-0 z-30 md:hidden safe-bottom"
          style={{
            background: 'rgba(3, 10, 10, 0.97)',
            backdropFilter: 'blur(20px)',
            borderTop: '1px solid rgba(3,83,82,0.22)',
          }}
        >
          <div className="flex items-center justify-around px-1 py-2">
            {MOBILE_NAV.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `mobile-nav-item ${isActive ? 'mobile-nav-active' : 'mobile-nav-inactive'}`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-medium mt-0.5">{label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
      </div>
    </div>
  );
}
