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
        'card-flip': 'card-flip 2s linear infinite',
      },
      keyframes: {
        'card-flip': {
          '0%': { 
            opacity: '0',
            transform: 'rotateY(0deg) scale(0.8)',
          },
          '10%': {
            opacity: '1',
            transform: 'rotateY(0deg) scale(1)',
          },
          '40%': {
            opacity: '1',
            transform: 'rotateY(180deg) scale(1)',
            backgroundColor: '#2d2d2d',
            borderColor: '#888',
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