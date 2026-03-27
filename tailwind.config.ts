import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "un-blue": "#009EDB",
      },
      boxShadow: {
        soft: "0 4px 18px rgba(0, 0, 0, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;
