/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // <-- important
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}; 