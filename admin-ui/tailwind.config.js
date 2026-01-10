module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#003366",
        secondary: "#004d99",
      },
      animation: {
        blob: "blob 7s infinite",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        ".backdrop-blur-sm": {
          "backdrop-filter": "blur(4px)",
        },
        ".backdrop-blur-md": {
          "backdrop-filter": "blur(12px)",
        },
        ".backdrop-blur-lg": {
          "backdrop-filter": "blur(16px)",
        },
        ".backdrop-blur-xl": {
          "backdrop-filter": "blur(24px)",
        },
      };
      addUtilities(newUtilities);
    },
  ],
};
