"use client";

import { useState } from "react";
import { getThumbnailUrl, getDownloadUrl, getImageUrl } from "@/lib/image-utils";
import { ImageLightbox } from "@/components/ui/image-lightbox";

export interface ImagePreviewProps {
  /** Original image URL (backend path, proxy path, or absolute). */
  src: string;
  /** Alt text for the image. */
  alt?: string;
  /** Extra CSS classes for the outer container. */
  className?: string;
  /** Max thumbnail dimension in px (default 400). */
  thumbnailSize?: number;
  /** Suggested download filename. */
  downloadFilename?: string;
  /** Show the download button below the thumbnail (default true). */
  showDownload?: boolean;
  /** Show the expand/popup button overlay (default true). */
  showExpand?: boolean;
  /** Tailwind aspect-ratio class (e.g. "aspect-video", "aspect-square"). */
  aspectRatio?: string;
  /** Extra CSS classes for the image itself. */
  imageClassName?: string;
}

/**
 * Standardized image preview component.
 *
 * - Displays an optimized WebP thumbnail via the backend thumbnail endpoint.
 * - Click to expand in a fullscreen lightbox.
 * - Optional download button for the original quality file.
 * - Error/loading states handled gracefully.
 */
export function ImagePreview({
  src,
  alt = "پیش‌نمایش",
  className = "",
  thumbnailSize = 400,
  downloadFilename,
  showDownload = true,
  showExpand = true,
  aspectRatio = "aspect-auto",
  imageClassName = "",
}: ImagePreviewProps) {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const thumbUrl = getThumbnailUrl(src, thumbnailSize);
  const dlUrl = getDownloadUrl(src);
  const fullUrl = getImageUrl(src);

  if (!src) return null;

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!dlUrl) return;
    const a = document.createElement("a");
    a.href = dlUrl;
    a.download = downloadFilename || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <>
      <div className={`relative group overflow-hidden rounded-lg bg-gray-100 ${className}`}>
        {/* Loading skeleton */}
        {!loaded && !error && (
          <div
            className={`absolute inset-0 animate-pulse bg-gray-200 ${aspectRatio}`}
          />
        )}

        {/* Error state */}
        {error ? (
          <div
            className={`flex flex-col items-center justify-center p-4 text-gray-400 ${aspectRatio}`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-8 h-8 mb-1"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5a2.25 2.25 0 002.25-2.25V5.25a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 003.75 21z"
              />
            </svg>
            <span className="text-xs">تصویر بارگذاری نشد</span>
          </div>
        ) : (
          <>
            {/* Thumbnail image */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={thumbUrl || fullUrl}
              alt={alt}
              onLoad={() => setLoaded(true)}
              onError={() => setError(true)}
              className={`w-full h-full object-cover transition-opacity duration-300 ${
                loaded ? "opacity-100" : "opacity-0"
              } ${aspectRatio} ${imageClassName}`}
              loading="lazy"
            />

            {/* Hover overlay with actions */}
            {(showExpand || showDownload) && (
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                {showExpand && (
                  <button
                    onClick={() => setLightboxOpen(true)}
                    className="p-2 rounded-full bg-white/90 hover:bg-white text-gray-800 shadow-md transition"
                    title="نمایش بزرگ"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-5 h-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9m11.25-5.25v4.5m0-4.5h-4.5m4.5 0L15 9m-11.25 11.25v-4.5m0 4.5h4.5m-4.5 0L9 15m11.25 5.25v-4.5m0 4.5h-4.5m4.5 0L15 15"
                      />
                    </svg>
                  </button>
                )}
                {showDownload && dlUrl && (
                  <button
                    onClick={handleDownload}
                    className="p-2 rounded-full bg-white/90 hover:bg-white text-gray-800 shadow-md transition"
                    title="دانلود فایل اصلی"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-5 h-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
                      />
                    </svg>
                  </button>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Lightbox */}
      {lightboxOpen && (
        <ImageLightbox
          src={src}
          alt={alt}
          downloadFilename={downloadFilename}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </>
  );
}
