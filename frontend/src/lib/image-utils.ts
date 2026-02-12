/**
 * Centralized image URL utility for Sheetaro.
 *
 * Backend returns URLs in several formats:
 *   - Relative without prefix:  "/files/templates/abc.png"
 *   - Relative with prefix:     "/api/v1/files/receipts/abc.png"
 *   - Absolute:                 "http://localhost:3005/api/v1/files/previews/dynamic_xxx.png"
 *   - External:                 "https://cdn.example.com/image.png"
 *
 * This utility normalises ALL of them into proxy paths (/api/proxy/v1/...)
 * that work from both the browser and the Next.js server inside Docker.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005";

/**
 * Convert any backend image path to a proxy-based URL.
 *
 * @returns A proxy URL like /api/proxy/v1/files/..., or the original external URL.
 */
export function getImageUrl(url?: string | null): string | undefined {
  if (!url) return undefined;

  // Step 1 — Absolute URL: strip the origin, keep only the path
  let path = url;
  if (url.startsWith("http://") || url.startsWith("https://")) {
    // Check if it contains /api/v1/ (i.e. points to our backend)
    const apiV1Index = url.indexOf("/api/v1/");
    if (apiV1Index !== -1) {
      path = url.substring(apiV1Index); // "/api/v1/files/previews/abc.png"
    } else {
      // Truly external URL — return as-is
      return url;
    }
  }

  // Step 2 — Strip the /api/v1 prefix if present so we have a clean relative path
  //   "/api/v1/files/receipts/abc.png" -> "/files/receipts/abc.png"
  //   "/files/templates/abc.png"       -> "/files/templates/abc.png"  (unchanged)
  if (path.startsWith("/api/v1/")) {
    path = path.substring("/api/v1".length); // "/files/receipts/abc.png"
  }

  // Step 3 — Ensure leading slash
  if (!path.startsWith("/")) {
    path = `/${path}`;
  }

  // Step 4 — Prefix with the proxy path
  return `/api/proxy/v1${path}`;
}

/**
 * Build a direct (non-proxied) backend URL.
 * Use only when the proxy is not available (e.g. external scripts, downloads).
 */
export function getDirectImageUrl(url?: string | null): string | undefined {
  if (!url) return undefined;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  const normalizedPath = url.startsWith("/") ? url : `/${url}`;
  return `${API_BASE_URL}/api/v1${normalizedPath}`;
}

/**
 * Extract a clean relative path from a backend URL for use with thumbnail/download endpoints.
 * e.g. "/api/v1/files/templates/abc.png"  -> "templates/abc.png"
 *      "/files/designs/uid/abc.png"       -> "designs/uid/abc.png"
 *      "http://host/api/v1/files/previews/abc.png" -> "previews/abc.png"
 */
function extractFilePath(url: string): string | null {
  if (!url) return null;

  let path = url;

  // Strip absolute URL prefix
  if (path.startsWith("http://") || path.startsWith("https://")) {
    const idx = path.indexOf("/api/v1/");
    if (idx !== -1) {
      path = path.substring(idx);
    } else {
      const filesIdx = path.indexOf("/files/");
      if (filesIdx !== -1) path = path.substring(filesIdx);
      else return null;
    }
  }

  // Strip API prefix
  if (path.startsWith("/api/v1/")) path = path.substring("/api/v1".length);
  if (path.startsWith("/api/proxy/v1/")) path = path.substring("/api/proxy/v1".length);

  // Strip /files/ prefix to get relative subpath
  if (path.startsWith("/files/")) path = path.substring("/files/".length);
  else if (path.startsWith("files/")) path = path.substring("files/".length);

  return path || null;
}

/**
 * Build a proxy URL for the optimized thumbnail of an image.
 * Uses the backend's /files/thumbnail/ endpoint.
 */
export function getThumbnailUrl(url?: string | null, maxSize = 400): string | undefined {
  if (!url) return undefined;
  const filePath = extractFilePath(url);
  if (!filePath) return getImageUrl(url);
  return `/api/proxy/v1/files/thumbnail/${filePath}?max_size=${maxSize}`;
}

/**
 * Build a proxy URL that triggers a browser download (Content-Disposition: attachment).
 */
export function getDownloadUrl(url?: string | null): string | undefined {
  if (!url) return undefined;
  const filePath = extractFilePath(url);
  if (!filePath) return getImageUrl(url);
  return `/api/proxy/v1/files/download/${filePath}`;
}
