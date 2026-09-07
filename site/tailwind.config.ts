import type { Config } from 'tailwindcss';

/**
 * Paleta extraída da captura de referência (analysis/color-palette.json):
 *   fundo        rgb(8, 6, 6)
 *   superfície   rgb(24, 20, 21)
 *   texto forte  rgb(242, 239, 240)
 *   texto        rgb(198, 191, 192)
 *   texto fraco  rgb(172, 168, 169)
 *   destaque     rgb(242, 53, 81)  /  hover rgb(241, 69, 95)
 */
const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        base: 'rgb(var(--base) / <alpha-value>)',
        surface: 'rgb(var(--surface) / <alpha-value>)',
        raised: 'rgb(var(--raised) / <alpha-value>)',
        line: 'rgb(var(--line) / <alpha-value>)',
        strong: 'rgb(var(--strong) / <alpha-value>)',
        body: 'rgb(var(--body) / <alpha-value>)',
        muted: 'rgb(var(--muted) / <alpha-value>)',
        accent: 'rgb(var(--accent) / <alpha-value>)',
        'accent-soft': 'rgb(var(--accent-soft) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Manrope', 'Helvetica Neue', 'system-ui', 'sans-serif'],
        mono: ['Inconsolata', 'JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      maxWidth: { content: '860px' },
      fontSize: {
        // Escala da captura: h3 13px/700, h4 18px/600, corpo 15px
        micro: ['13px', { lineHeight: '18px', letterSpacing: '1.04px' }],
        body: ['15px', { lineHeight: '26px' }],
      },
      keyframes: {
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(6px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-down': {
          from: { opacity: '0', maxHeight: '0' },
          to: { opacity: '1', maxHeight: '1200px' },
        },
      },
      animation: {
        'fade-up': 'fade-up .28s ease-out both',
        'slide-down': 'slide-down .22s ease-out both',
      },
    },
  },
  plugins: [],
};

export default config;
