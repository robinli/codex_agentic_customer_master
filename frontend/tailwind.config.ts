import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#10212E",
        mist: "#F4F7F2",
        brass: "#B78628",
        spruce: "#25594A",
        blush: "#F2E3D7"
      },
      fontFamily: {
        sans: ["'IBM Plex Sans TC'", "sans-serif"],
        display: ["'DM Serif Display'", "serif"]
      }
    }
  },
  plugins: []
};

export default config;

