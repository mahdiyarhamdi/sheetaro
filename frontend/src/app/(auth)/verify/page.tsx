"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthLayout } from "@/components/layout";
import { Button, Card, CardContent } from "@/components/ui";
import { useAuth } from "@/hooks/useAuth";
import { Send, RefreshCw, Copy, Check, ArrowRight } from "lucide-react";
import { toPersianNumber } from "@/lib/utils";

export default function VerifyTelegramPage() {
  const router = useRouter();
  const {
    user,
    isAuthenticated,
    generateTelegramLink,
    telegramLinkData,
    isGeneratingTelegramLink,
  } = useAuth();

  const [copied, setCopied] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/verify");
    }
  }, [isAuthenticated, router]);

  // Generate OTP on mount
  useEffect(() => {
    if (isAuthenticated && !telegramLinkData) {
      generateTelegramLink();
    }
  }, [isAuthenticated, telegramLinkData, generateTelegramLink]);

  // Countdown timer
  useEffect(() => {
    if (telegramLinkData?.expires_at) {
      const expiresAt = new Date(telegramLinkData.expires_at).getTime();
      
      const timer = setInterval(() => {
        const now = Date.now();
        const diff = Math.max(0, Math.floor((expiresAt - now) / 1000));
        setTimeLeft(diff);
        
        if (diff === 0) {
          clearInterval(timer);
        }
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [telegramLinkData]);

  const handleCopy = async () => {
    if (telegramLinkData?.otp) {
      await navigator.clipboard.writeText(telegramLinkData.otp);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRefresh = () => {
    generateTelegramLink();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${toPersianNumber(mins)}:${toPersianNumber(secs.toString().padStart(2, "0"))}`;
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <AuthLayout
      title="اتصال حساب تلگرام"
      description="با اتصال تلگرام می‌توانید از هر دو پلتفرم استفاده کنید"
    >
      <div className="space-y-6">
        {/* Instructions */}
        <div className="text-center">
          <p className="text-muted text-sm mb-4">
            برای اتصال حساب تلگرام، مراحل زیر را دنبال کنید:
          </p>
        </div>

        {/* OTP Card */}
        <Card variant="bordered">
          <CardContent className="py-6">
            {isGeneratingTelegramLink ? (
              <div className="flex items-center justify-center py-4">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : telegramLinkData?.otp ? (
              <div className="text-center">
                <p className="text-sm text-muted mb-3">کد تایید شما:</p>
                <div className="flex items-center justify-center gap-2 mb-3">
                  <span
                    className="text-3xl font-bold text-primary tracking-widest"
                    dir="ltr"
                  >
                    {telegramLinkData.otp}
                  </span>
                  <button
                    onClick={handleCopy}
                    className="p-2 hover:bg-accent rounded-lg transition-colors"
                    title="کپی کد"
                  >
                    {copied ? (
                      <Check className="w-5 h-5 text-success" />
                    ) : (
                      <Copy className="w-5 h-5 text-muted" />
                    )}
                  </button>
                </div>
                
                {/* Timer */}
                {timeLeft > 0 ? (
                  <p className="text-sm text-muted">
                    اعتبار کد:{" "}
                    <span className="font-medium text-foreground">
                      {formatTime(timeLeft)}
                    </span>
                  </p>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-danger">کد منقضی شده است</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRefresh}
                      leftIcon={<RefreshCw className="w-4 h-4" />}
                    >
                      دریافت کد جدید
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center">
                <p className="text-sm text-danger mb-3">
                  خطا در دریافت کد
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  leftIcon={<RefreshCw className="w-4 h-4" />}
                >
                  تلاش مجدد
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Steps */}
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-accent rounded-lg">
            <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm font-bold shrink-0">
              ۱
            </div>
            <p className="text-sm">
              ربات{" "}
              <a
                href="https://t.me/sheetarobot"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary font-medium hover:underline"
              >
                @sheetarobot
              </a>{" "}
              را در تلگرام باز کنید
            </p>
          </div>
          
          <div className="flex items-start gap-3 p-3 bg-accent rounded-lg">
            <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm font-bold shrink-0">
              ۲
            </div>
            <p className="text-sm">
              دستور{" "}
              <code className="bg-surface px-1.5 py-0.5 rounded text-primary font-mono">
                /linkweb
              </code>{" "}
              را ارسال کنید
            </p>
          </div>
          
          <div className="flex items-start gap-3 p-3 bg-accent rounded-lg">
            <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm font-bold shrink-0">
              ۳
            </div>
            <p className="text-sm">
              کد ۶ رقمی بالا را در ربات وارد کنید
            </p>
          </div>
        </div>

        {/* Open Telegram Button */}
        <a
          href="https://t.me/sheetarobot?start=linkweb"
          target="_blank"
          rel="noopener noreferrer"
          className="block"
        >
          <Button
            variant="primary"
            className="w-full"
            leftIcon={<Send className="w-4 h-4" />}
          >
            باز کردن ربات تلگرام
          </Button>
        </a>

        {/* Skip */}
        <button
          onClick={() => router.push("/")}
          className="flex items-center justify-center gap-1 w-full text-sm text-muted hover:text-foreground transition-colors"
        >
          <span>بعداً انجام می‌دهم</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </AuthLayout>
  );
}

