"use client";

import { useCallback, useEffect, useState } from "react";
import { getImageUrl, getDownloadUrl } from "@/lib/image-utils";

interface ImageLightboxProps {
  src: string;
  alt?: string;
  downloadFilename?: string;
  onClose: () => void;
}

/**
 * Fullscreen lightbox modal for viewing images at full resolution.
 * Features: dark overlay, Escape-to-close, download button, zoom toggle.
 */
export function ImageLightbox({
  src,
  alt = "تصویر",
  downloadFilename,
  onClose,
}: ImageLightboxProps) {
  const [zoomed, setZoomed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const fullUrl = getImageUrl(src);
  const dlUrl = getDownloadUrl(src);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [handleKeyDown]);

  const handleDownload = () => {
    if (!dlUrl) return;
    const a = document.createElement("a");
    a.href = dlUrl;
    a.download = downloadFilename || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/85"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {/* Toolbar */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-black/50 to-transparent">
        <div className="text-white text-sm opacity-80 truncate max-w-[50%]">
          {alt}
        </div>
        <div className="flex items-center gap-3">
          {/* Zoom toggle */}
          <button
            onClick={() => setZoomed(!zoomed)}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition"
            title={zoomed ? "بازگشت به اندازه اصلی" : "بزرگنمایی"}
          >
            {zoomed ? (
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
                  d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM13.5 10.5h-6"
                />
              </svg>
            ) : (
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
                  d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM10.5 7.5v6m3-3h-6"
                />
              </svg>
            )}
          </button>

          {/* Download button */}
          {dlUrl && (
            <button
              onClick={handleDownload}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition"
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

          {/* Close button */}
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition"
            title="بستن"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Image container */}
      <div
        className={`relative max-h-[90vh] max-w-[95vw] transition-transform duration-200 ${
          zoomed ? "cursor-zoom-out scale-150" : "cursor-zoom-in"
        }`}
        onClick={() => setZoomed(!zoomed)}
      >
        {!loaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
          </div>
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={fullUrl}
          alt={alt}
          onLoad={() => setLoaded(true)}
          className={`max-h-[90vh] max-w-[95vw] object-contain rounded-lg shadow-2xl transition-opacity duration-300 ${
            loaded ? "opacity-100" : "opacity-0"
          }`}
          draggable={false}
        />
      </div>
    </div>
  );
}
