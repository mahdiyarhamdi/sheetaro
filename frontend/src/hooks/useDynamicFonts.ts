"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi, SystemFont } from "@/lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005";

/**
 * Get full URL for a font file
 */
const getFontUrl = (fileUrl: string | null | undefined): string | null => {
  if (!fileUrl) return null;

  // If already absolute URL, return as is
  if (fileUrl.startsWith("http")) return fileUrl;

  // Add /api/v1 prefix if not present
  const apiPath = fileUrl.startsWith("/api/v1") ? fileUrl : `/api/v1${fileUrl}`;
  return `${API_BASE_URL}${apiPath}`;
};

/**
 * Get font format from file extension
 */
const getFontFormat = (fileUrl: string): string => {
  const ext = fileUrl.split(".").pop()?.toLowerCase();
  switch (ext) {
    case "woff2":
      return "woff2";
    case "woff":
      return "woff";
    case "ttf":
      return "truetype";
    case "otf":
      return "opentype";
    default:
      return "truetype";
  }
};

/**
 * Hook to dynamically load system fonts from API
 * Creates @font-face rules and injects them into the document head
 */
export function useDynamicFonts() {
  // Fetch active fonts from API
  const { data: fonts, isLoading, error } = useQuery({
    queryKey: ["fonts-active"],
    queryFn: async () => {
      const response = await adminApi.getFonts(true);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Load fonts dynamically via @font-face
  useEffect(() => {
    if (!fonts || fonts.length === 0) return;

    // Create a unique style element for dynamic fonts
    const styleId = "dynamic-fonts-style";
    let styleEl = document.getElementById(styleId) as HTMLStyleElement | null;

    if (!styleEl) {
      styleEl = document.createElement("style");
      styleEl.id = styleId;
      document.head.appendChild(styleEl);
    }

    // Build @font-face rules for all fonts and their variants
    const fontFaceRules: string[] = [];

    fonts.forEach((font: SystemFont) => {
      // If font has a main file_url, load it as default
      const mainFontUrl = getFontUrl(font.file_url);
      if (mainFontUrl) {
        const format = getFontFormat(font.file_url || "");
        fontFaceRules.push(`
          @font-face {
            font-family: '${font.name}';
            src: url('${mainFontUrl}') format('${format}');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
          }
        `);
      }

      // Load each variant with its specific weight and style
      if (font.variants && font.variants.length > 0) {
        font.variants.forEach((variant) => {
          // Try woff2 first, then woff, then ttf
          const variantUrl =
            getFontUrl(variant.file_woff2) ||
            getFontUrl(variant.file_woff) ||
            getFontUrl(variant.file_url);

          if (variantUrl) {
            const format = getFontFormat(variantUrl);
            fontFaceRules.push(`
              @font-face {
                font-family: '${font.name}';
                src: url('${variantUrl}') format('${format}');
                font-weight: ${variant.weight};
                font-style: ${variant.style || "normal"};
                font-display: swap;
              }
            `);
          }
        });
      }
    });

    // Set the style content
    styleEl.textContent = fontFaceRules.join("\n");

    // Cleanup function - remove style element when component unmounts
    return () => {
      // Don't remove the style element on cleanup to keep fonts available
      // The style element is reused across component remounts
    };
  }, [fonts]);

  return { fonts, isLoading, error };
}

/**
 * Component to load fonts globally - use in layout or provider
 */
export function FontLoader() {
  useDynamicFonts();
  return null;
}

export default useDynamicFonts;
