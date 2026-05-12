import type { Config } from "tailwindcss";

/**
 * DayLight design tokens.
 * Neutral palette: gold/amber for highlights, warm grays for text,
 * black/white for structure. NO partisan red/blue dominance.
 * Party indicators are intentionally muted, equal-weight, accessible.
 */
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        daylight: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
        },
        ink: {
          50: "#fafaf9",
          100: "#f5f5f4",
          200: "#e7e5e4",
          300: "#d6d3d1",
          400: "#a8a29e",
          500: "#78716c",
          600: "#57534e",
          700: "#44403c",
          800: "#292524",
          900: "#1c1917",
          950: "#0c0a09",
        },
        // Equal-weight party tones — both desaturated, similar luminance.
        // Goal: party is a small fact, not a flag.
        party: {
          dem: "#5b6b8a",
          rep: "#a36a6a",
          ind: "#7c7766",
          npa: "#7c7766",
          other: "#7c7766",
        },
        flag: {
          alignment: "#b45309",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Lora", "Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      maxWidth: {
        prose: "68ch",
      },
      boxShadow: {
        card: "0 1px 2px rgba(28,25,23,0.06), 0 4px 16px rgba(28,25,23,0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
