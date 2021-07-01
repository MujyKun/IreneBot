const colors = require("tailwindcss/colors");

module.exports = {
  purge: ["./public/index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  darkMode: false, // or 'media' or 'class'
  theme: {
    borderWidth: {
      1: "1px",
    },
    colors: {
      ...colors,
      blurple: {
        DEFAULT: "#7289d9",
        dark: "#50619a",
      },
      theme: {
        DEFAULT: "#070513",
        alt: "#0c0b17",
        secondary: "#2E3745",
      },
    },
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
