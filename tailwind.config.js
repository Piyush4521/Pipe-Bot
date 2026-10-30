/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          50: '#F8F9FA',
          100: '#F1F3F5',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#020617',
        },
        brand: {
          orange: '#EA580C',      // High-visibility Industrial Safety Orange
          'orange-hover': '#C2410C',
          'orange-light': '#FFF7ED',
          'orange-border': '#FDBA74',
        },
        status: {
          healthy: '#16A34A',
          'healthy-bg': '#F0FDF4',
          'healthy-border': '#86EFAC',
          warning: '#D97706',
          'warning-bg': '#FFFBEB',
          'warning-border': '#FDE68A',
          critical: '#DC2626',
          'critical-bg': '#FEF2F2',
          'critical-border': '#FECACA',
          neutral: '#64748B',
          'neutral-bg': '#F8F9FA',
          'neutral-border': '#CBD5E1',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"SF Mono"',
          'Menlo',
          'Monaco',
          'Consolas',
          '"Courier New"',
          'monospace',
        ],
      },
      boxShadow: {
        'industrial': '1px 1px 0px 0px #0F172A',
        'industrial-md': '2px 2px 0px 0px #0F172A',
        'industrial-sm': '1px 1px 0px 0px #CBD5E1',
      },
      borderRadius: {
        DEFAULT: '2px',
        none: '0px',
        sm: '2px',
        md: '4px',
        lg: '6px',
        // Note: Strict restriction - No pill/excessive radius allowed
      },
    },
  },
  plugins: [],
}

