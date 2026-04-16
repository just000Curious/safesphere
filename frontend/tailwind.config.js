/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#7C3AED", // Deep Purple
        danger: "#E11D48",  // Neon Red
        success: "#10B981", // Emerald Green
        dark: "#0F172A",    // Very Dark Gray
        darker: "#0B0F19",  // Deep Background
        textLight: "#F8FAFC",
        textMuted: "#94A3B8"
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
