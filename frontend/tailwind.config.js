/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        // ── Brand: Primary Teal ────────────────────────
        teal: {
          50:  '#e6f4f4',
          100: '#b3dede',
          200: '#80c8c8',
          300: '#4db2b2',
          400: '#269c9c',
          500: '#035352',   // PRIMARY BRAND TEAL
          600: '#024544',
          700: '#023736',
          800: '#012a29',
          900: '#011c1b',
          950: '#000d0c',
        },
        // ── Brand: Warm Cream ──────────────────────────
        cream: {
          50:  '#fffef8',
          100: '#fefcec',
          200: '#fdf8d9',
          300: '#fbf2bf',
          400: '#f8eba6',
          500: '#F3E8BC',   // PRIMARY BRAND CREAM
          600: '#e8d89a',
          700: '#d4be6a',
          800: '#b89f3e',
          900: '#8a751c',
          950: '#5c4d08',
        },
        // ── Legacy cyber (keep for backwards compat) ──
        cyber: {
          50:  '#e8fff9',
          100: '#b3ffe8',
          200: '#66ffd1',
          300: '#00ffb8',
          400: '#00e6a3',
          500: '#00cc8f',
          600: '#00997a',
          700: '#006655',
          800: '#003d33',
          900: '#001a15',
        },
        // ── Dark scale ────────────────────────────────
        dark: {
          50:  '#e4eaee',
          100: '#bccad2',
          200: '#8da8b5',
          300: '#5e8699',
          400: '#3a6878',
          500: '#1e3d4a',
          600: '#16303b',
          700: '#0e232c',
          800: '#08161d',
          900: '#04090e',
          950: '#020507',
        },
      },
      animation: {
        'pulse-slow':  'pulseSlow 2.5s ease-in-out infinite',
        'pulse-dot':   'pulseDot 2s ease-in-out infinite',
        'fade-in':     'fadeIn 0.35s ease-out',
        'slide-in':    'slideIn 0.3s ease-out',
        'slide-right': 'slideRight 0.35s cubic-bezier(0.16,1,0.3,1)',
        'shimmer':     'shimmer 2s infinite',
        'radar':       'radarSpin 4s linear infinite',
        'float':       'float 6s ease-in-out infinite',
        'glow-pulse':  'glowPulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%':   { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideRight: {
          '0%':   { opacity: '0', transform: 'translateX(24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        pulseSlow: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.35' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%':      { opacity: '0.5', transform: 'scale(0.8)' },
        },
        radarSpin: {
          '0%':   { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-6px)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 12px rgba(3,83,82,0.4)' },
          '50%':      { boxShadow: '0 0 28px rgba(3,83,82,0.8), 0 0 50px rgba(3,83,82,0.3)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
