"use client";

import Image, { ImageProps } from "next/image";

/**
 * OptimizedImage - A wrapper around Next.js Image that handles external URLs properly.
 * For external URLs (non-localhost), it disables server-side optimization to avoid
 * Docker network issues where the frontend container can't reach external IPs.
 */
export function OptimizedImage({ src, ...props }: ImageProps) {
  // Check if the URL is external (not localhost or relative)
  const isExternal = typeof src === 'string' && 
    (src.startsWith('http://') || src.startsWith('https://')) &&
    !src.includes('localhost');
  
  return (
    <Image
      src={src}
      unoptimized={isExternal}
      {...props}
    />
  );
}

export default OptimizedImage;
