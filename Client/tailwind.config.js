/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoalGray: '#555555',
        slateGray: '#708090',
        darkGraphite: '#4A4A4A',
        darkColor: '#1f1f1f',
        lightGray: '#D3D3D3',
        cream: '#efe5e5',
      },
    },
  },
  plugins: [],
}

