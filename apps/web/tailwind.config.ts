import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0a0d12",
        panel: "#11161e",
        surface: "#171e28",
        line: "#27313d",
        lime: "#c8f169",
        muted: "#8b98a8",
      },
      fontFamily: {
        display: ["Space Grotesk", "Inter", "sans-serif"],
        sans: ["Inter", "sans-serif"],
      },
      boxShadow: {
        card: "0 18px 54px rgba(0,0,0,.24)",
        glow: "0 0 0 1px rgba(200,241,105,.18), 0 8px 32px rgba(200,241,105,.08)",
      },
      backgroundImage: {
        "blueprint-grid": "linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
