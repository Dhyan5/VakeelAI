/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#FAFAF9',
        body: '#1E293B',
        accent: '#1E3A8A', // Deep navy
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        kannada: ['"Noto Sans Kannada"', 'sans-serif'],
        devanagari: ['"Noto Sans Devanagari"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
