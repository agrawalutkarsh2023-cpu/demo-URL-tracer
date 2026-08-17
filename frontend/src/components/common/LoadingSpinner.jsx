import { Shield } from 'lucide-react';

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-5">
      {/* Animated shield ring */}
      <div className="relative w-16 h-16">
        <svg className="w-full h-full" viewBox="0 0 64 64">
          {/* Track */}
          <circle
            cx="32" cy="32" r="28"
            fill="none"
            stroke="rgba(3,83,82,0.15)"
            strokeWidth="3"
          />
          {/* Spinning arc */}
          <circle
            cx="32" cy="32" r="28"
            fill="none"
            stroke="#035352"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="44 132"
            style={{ transformOrigin: 'center', animation: 'radarSpin 1.2s linear infinite' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <Shield className="w-6 h-6" style={{ color: '#F3E8BC' }} />
        </div>
      </div>
      <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>{message}</p>
      <p className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>NetTrace Security</p>
    </div>
  );
}
