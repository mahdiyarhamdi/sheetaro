"use client";

import { useState, useEffect, useCallback } from "react";
import { X, Download, Share, Plus } from "lucide-react";
import { Button } from "@/components/ui";

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

const DISMISSED_KEY = "pwa_install_dismissed";

function isIos() {
  if (typeof navigator === "undefined") return false;
  return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

function isInStandaloneMode() {
  if (typeof window === "undefined") return false;
  return (
    ("standalone" in window.navigator && (window.navigator as unknown as { standalone: boolean }).standalone) ||
    window.matchMedia("(display-mode: standalone)").matches
  );
}

function isMobile() {
  if (typeof navigator === "undefined") return false;
  return /android|iphone|ipad|ipod|mobile/i.test(navigator.userAgent);
}

export function PwaInstallPrompt() {
  const [show, setShow] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isIosDevice, setIsIosDevice] = useState(false);

  useEffect(() => {
    if (!isMobile()) return;
    if (isInStandaloneMode()) return;

    const dismissed = localStorage.getItem(DISMISSED_KEY);
    if (dismissed) {
      const dismissedAt = parseInt(dismissed, 10);
      const threeDays = 3 * 24 * 60 * 60 * 1000;
      if (Date.now() - dismissedAt < threeDays) return;
    }

    if (isIos()) {
      setIsIosDevice(true);
      const timer = setTimeout(() => setShow(true), 2000);
      return () => clearTimeout(timer);
    }

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setTimeout(() => setShow(true), 2000);
    };

    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setShow(false);
    }
    setDeferredPrompt(null);
  }, [deferredPrompt]);

  const handleDismiss = useCallback(() => {
    setShow(false);
    localStorage.setItem(DISMISSED_KEY, Date.now().toString());
  }, []);

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-end justify-center p-4 pointer-events-none">
      {/* backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm pointer-events-auto animate-in fade-in duration-300"
        onClick={handleDismiss}
      />

      {/* prompt card */}
      <div className="relative w-full max-w-sm bg-white rounded-2xl shadow-2xl pointer-events-auto animate-in slide-in-from-bottom duration-300 mb-safe">
        {/* close button */}
        <button
          onClick={handleDismiss}
          className="absolute top-3 left-3 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>

        <div className="p-6 pt-8 text-center">
          {/* app icon */}
          <div className="w-20 h-20 rounded-[22px] mx-auto mb-5 bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/30">
            <span className="text-white text-4xl font-black leading-none">S</span>
          </div>

          <h3 className="text-lg font-bold text-foreground mb-2">
            شیتارو را نصب کنید
          </h3>
          <p className="text-sm text-muted leading-relaxed mb-6">
            با اضافه کردن شیتارو به صفحه اصلی، دسترسی سریع‌تر و تجربه بهتری خواهید داشت.
          </p>

          {isIosDevice ? (
            <div className="space-y-3">
              <div className="bg-gray-50 rounded-xl p-4 text-right space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center shrink-0">
                    <Share className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-foreground">
                    <span className="font-semibold">۱.</span> روی دکمه <span className="font-semibold">Share</span> (اشتراک‌گذاری) بزنید
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center shrink-0">
                    <Plus className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-foreground">
                    <span className="font-semibold">۲.</span> گزینه <span className="font-semibold">Add to Home Screen</span> را انتخاب کنید
                  </p>
                </div>
              </div>
              <Button variant="outline" className="w-full" onClick={handleDismiss}>
                متوجه شدم
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <Button
                variant="primary"
                className="w-full"
                size="lg"
                onClick={handleInstall}
                leftIcon={<Download className="w-5 h-5" />}
              >
                نصب اپلیکیشن
              </Button>
              <button
                onClick={handleDismiss}
                className="text-sm text-muted hover:text-foreground transition-colors w-full py-2"
              >
                فعلاً نه، بعداً
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
