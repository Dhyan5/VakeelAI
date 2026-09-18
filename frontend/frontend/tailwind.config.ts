import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#FAFAF9',
        body: '#1E293B',
        accent: '#1E3A8A',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        kannada: ['"Noto Sans Kannada"', 'sans-serif'],
        devanagari: ['"Noto Sans Devanagari"', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
