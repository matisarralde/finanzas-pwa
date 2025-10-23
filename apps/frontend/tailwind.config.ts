import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(0 0% 100%)",
        foreground: "hsl(222.2 84% 4.9%)",
        muted: "hsl(210 40% 96.1%)",
        border: "hsl(214.3 31.8% 91.4%)"
      },
      borderRadius: {
        xl: "0.75rem",
      },
    },
  },
  plugins: [],
} satisfies Config;

