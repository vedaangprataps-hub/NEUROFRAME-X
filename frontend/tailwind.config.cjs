/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#05070D',
        surface: '#0B1020',
        primary: '#00E5FF',
        secondary: '#9D4EDD',
        success: '#00FFB2',
        text: '#F5F7FF',
        muted: '#8892A6',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        neon: '0 0 8px rgba(0, 229, 255, 0.6)',
        neonViolet: '0 0 8px rgba(157, 78, 221, 0.6)',
      },
      animation: {
        'gradient-x': 'gradient-x 8s ease infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
  plugins: [],
}
