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
        dark: {
          50:  '#e8eaf0',
          100: '#c8cdd8',
          200: '#9099b0',
          300: '#586688',
          400: '#2d3a5c',
          500: '#1a2340',
          600: '#141c34',
          700: '#0e1428',
          800: '#080d1c',
          900: '#040710',
          950: '#020408',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
