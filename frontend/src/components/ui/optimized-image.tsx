"use client";

import Image, { ImageProps } from "next/image";

/**
 * OptimizedImage - A wrapper around Next.js Image that handles API and external URLs.
 *
 * Disables server-side image optimization for:
 *   - API-served images (/api/proxy/..., /api/v1/files/...) -- the optimizer
 *     cannot reliably fetch these from inside the Docker container.
 *   - External URLs (non-localhost http/https) -- same Docker networking issue.
 *
 * Only local static assets (e.g. /images/logo.png) go through the optimizer.
 */
export function OptimizedImage({ src, ...props }: ImageProps) {
  const shouldSkipOptimization = typeof src === "string" && (
    // API-served images (proxy or direct)
    src.startsWith("/api/") ||
    // External absolute URLs
    ((src.startsWith("http://") || src.startsWith("https://")) && !src.includes("localhost"))
  );

  return (
    <Image
      src={src}
      unoptimized={shouldSkipOptimization}
      {...props}
    />
  );
}

export default OptimizedImage;
