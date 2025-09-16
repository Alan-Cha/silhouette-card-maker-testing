/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.{html,js,jsx,ts,tsx}",
    "./src/**/*.{html,js,jsx,ts,tsx}",
    "./styles/**/*.{css,scss}",
  ],
  exclude: [
    '**/node_modules/**',
    './node_modules/**',
  ],
  theme: {
    extend: {
      colors: {
        'primary': {
          light: '#CBD5E1',   // Light gray for borders and accents
          DEFAULT: '#F1F5F9', // White for primary content
          dark: '#FFFFFF',    // Pure white for headers and emphasis
        },
        'surface': {
          light: '#2A303C',   // Lighter slate for hover states
          DEFAULT: '#1E232F', // Main background (medium dark)
          dark: '#16181D',    // Darker for components
        },
        'content': {
          light: '#CBD5E1',   // Light gray for secondary text
          DEFAULT: '#F1F5F9', // Nearly white for primary text
          dark: '#FFFFFF',    // Pure white for headers
        }
      },
      animation: {
        'card-slide-1': 'card-slide 2s ease-in-out infinite',
        'card-slide-2': 'card-slide 2s ease-in-out infinite 0.66s',
        'card-slide-3': 'card-slide 2s ease-in-out infinite 1.33s',
      },
      keyframes: {
        'card-slide': {
          '0%': {
            opacity: '0',
            transform: 'translateY(-100%) translateX(-50%) rotate(-15deg)',
          },
          '25%, 35%': {
            opacity: '1',
            transform: 'translateY(0) translateX(0) rotate(0deg)',
          },
          '60%, 100%': {
            opacity: '0',
            transform: 'translateY(100%) translateX(50%) rotate(15deg)',
          },
        },
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.backface-visible': {
          'backface-visibility': 'visible',
        },
        '.backface-hidden': {
          'backface-visibility': 'hidden',
        },
        '.preserve-3d': {
          'transform-style': 'preserve-3d',
        },
      })
    },
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
  ],
}