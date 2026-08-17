import { Link } from 'react-router-dom';
import { Home, ShieldAlert, Globe, FileSearch, Brain, FileBarChart2, Shield, Mail } from 'lucide-react';
import usePageMeta from '../hooks/usePageMeta';

export default function NotFound() {
  usePageMeta('404 — Page Not Found', 'The page you are looking for does not exist. Return to NetTrace Security dashboard.');

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'var(--bg-base)' }}
    >
      <div className="text-center max-w-2xl mx-auto animate-fade-in">

        {/* Glitch 404 */}
        <div className="relative mb-6 select-none">
          <span
            className="not-found-glitch text-[10rem] md:text-[14rem] font-black leading-none"
            data-text="404"
            style={{
              background: 'linear-gradient(180deg, rgba(3,83,82,0.85) 0%, rgba(3,83,82,0.15) 100%)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
            }}
          >
            404
          </span>
          <div className="absolute inset-0 not-found-scanline pointer-events-none" />
        </div>

        {/* Icon + Message */}
        <div className="flex items-center justify-center gap-3 mb-4">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'rgba(3,83,82,0.15)', border: '1px solid rgba(3,83,82,0.35)' }}
          >
            <Shield className="w-5 h-5" style={{ color: '#F3E8BC' }} />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: '#F3E8BC' }}>Page Not Found</h1>
        </div>

        <p className="text-sm leading-relaxed mb-2" style={{ color: 'var(--text-secondary)' }}>
          The route you're looking for doesn't exist in this system.
        </p>
        <p className="text-xs font-mono mb-10" style={{ color: 'var(--text-muted)' }}>
          ERROR_CODE: 404 · ROUTE_NOT_REGISTERED · NETTRACE_SECURITY
        </p>

        {/* Primary CTA */}
        <Link to="/" className="btn-primary inline-flex px-6 py-3 text-sm mb-10">
          <Home className="w-4 h-4" />
          Back to Dashboard
        </Link>

        {/* Nav links */}
        <div className="mt-4">
          <p className="text-xs uppercase tracking-widest font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>
            Or navigate to
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { to: '/attacks',         label: 'Attack Explorer', icon: ShieldAlert  },
              { to: '/ip-intelligence', label: 'IP Intelligence', icon: Globe        },
              { to: '/pcap',            label: 'PCAP Analysis',   icon: FileSearch   },
              { to: '/ml',              label: 'ML Intelligence', icon: Brain        },
              { to: '/reports',         label: 'Reports',         icon: FileBarChart2},
              { to: '/contact',         label: 'Contact Us',      icon: Mail         },
            ].map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150"
                style={{
                  background: 'rgba(3,83,82,0.08)',
                  border: '1px solid rgba(3,83,82,0.22)',
                  color: 'var(--text-secondary)',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(3,83,82,0.18)';
                  e.currentTarget.style.borderColor = 'rgba(3,83,82,0.45)';
                  e.currentTarget.style.color = '#F3E8BC';
                  e.currentTarget.style.transform = 'scale(1.03)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(3,83,82,0.08)';
                  e.currentTarget.style.borderColor = 'rgba(3,83,82,0.22)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{label}</span>
              </Link>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
