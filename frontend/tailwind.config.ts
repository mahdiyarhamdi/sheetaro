import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary green palette from logo
        primary: {
          50: "#E8F5E9",
          100: "#C8E6C9",
          200: "#A5D6A7",
          300: "#81C784",
          400: "#66BB6A",
          500: "#4CAF50",
          600: "#43A047",
          700: "#388E3C",
          800: "#2E7D32",
          900: "#1B5E20",
          DEFAULT: "#2D7D46",
        },
        // Background colors
        background: "#F8FAF8",
        surface: "#FFFFFF",
        // Text colors
        foreground: "#1A1A1A",
        muted: {
          DEFAULT: "#6B7280",
          foreground: "#9CA3AF",
        },
        // Accent colors
        accent: {
          DEFAULT: "#E8F5E9",
          foreground: "#1B5E20",
        },
        // Status colors
        success: {
          DEFAULT: "#22C55E",
          light: "#DCFCE7",
        },
        warning: {
          DEFAULT: "#F59E0B",
          light: "#FEF3C7",
        },
        danger: {
          DEFAULT: "#EF4444",
          light: "#FEE2E2",
        },
        info: {
          DEFAULT: "#3B82F6",
          light: "#DBEAFE",
        },
        // Border colors
        border: "#E5E7EB",
        input: "#D1D5DB",
        ring: "#2D7D46",
      },
      fontFamily: {
        sans: ["IRANYekan", "Tahoma", "Arial", "sans-serif"],
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.25rem",
      },
      boxShadow: {
        soft: "0 2px 8px rgba(0, 0, 0, 0.06)",
        medium: "0 4px 16px rgba(0, 0, 0, 0.08)",
        strong: "0 8px 32px rgba(0, 0, 0, 0.12)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        spin: "spin 1s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideDown: {
          "0%": { transform: "translateY(-10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;

