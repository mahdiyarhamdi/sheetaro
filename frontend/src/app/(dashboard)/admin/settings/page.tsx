"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { proxyApi } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  PageLoading,
  Input,
} from "@/components/ui";
import {
  Settings,
  ArrowRight,
  CreditCard,
  Percent,
  Save,
  Bell,
  Globe,
  Database,
  Wifi,
  WifiOff,
  RefreshCw,
  Trash2,
  Zap,
  Activity,
} from "lucide-react";
import toast from "react-hot-toast";
import { cn, toPersianNumber } from "@/lib/utils";

export default function SettingsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);

  // Form states
  const [cardNumber, setCardNumber] = useState("");
  const [cardHolder, setCardHolder] = useState("");
  const [commissionRate, setCommissionRate] = useState("10");
  const [validationPrice, setValidationPrice] = useState("50000");

  // Proxy states
  const [proxyLink, setProxyLink] = useState("");
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; latency_ms: number } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  // Fetch proxy status
  const { data: proxyStatus, refetch: refetchProxy } = useQuery({
    queryKey: ["proxy-status"],
    queryFn: async () => {
      const res = await proxyApi.getStatus();
      return res.data;
    },
    enabled: isAdmin,
    refetchInterval: false,
  });

  // Set proxy link from server when loaded
  useEffect(() => {
    if (proxyStatus?.link && !proxyLink) {
      setProxyLink(proxyStatus.link);
    }
  }, [proxyStatus, proxyLink]);

  // Save proxy mutation
  const saveProxyMutation = useMutation({
    mutationFn: async (link: string) => {
      const res = await proxyApi.setLink(link);
      return res.data;
    },
    onSuccess: () => {
      toast.success("لینک پروکسی ذخیره شد. حالا «تست اتصال» را بزنید.");
      refetchProxy();
      setTestResult(null);
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "خطا در ذخیره لینک پروکسی");
    },
  });

  // Remove proxy mutation
  const removeProxyMutation = useMutation({
    mutationFn: () => proxyApi.remove(),
    onSuccess: () => {
      toast.success("پروکسی حذف شد");
      setProxyLink("");
      setTestResult(null);
      refetchProxy();
    },
    onError: () => toast.error("خطا در حذف پروکسی"),
  });

  // Restart services mutation
  const restartMutation = useMutation({
    mutationFn: async () => {
      const res = await proxyApi.restart();
      return res.data;
    },
    onSuccess: (data) => {
      toast.success(data.message || "سیگنال ری‌استارت ارسال شد");
    },
    onError: () => toast.error("خطا در ارسال سیگنال ری‌استارت"),
  });

  const handleTestProxy = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await proxyApi.test();
      setTestResult(res.data);
      if (res.data.success) {
        toast.success(`اتصال موفق - ${res.data.latency_ms}ms`);
      } else {
        toast.error(`اتصال ناموفق: ${res.data.message}`);
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "خطا در تست پروکسی";
      setTestResult({ success: false, message: msg, latency_ms: 0 });
      toast.error(msg);
    } finally {
      setIsTesting(false);
    }
  };

  const handleSaveProxy = () => {
    if (!proxyLink.trim()) {
      toast.error("لطفاً لینک V2Ray را وارد کنید");
      return;
    }
    saveProxyMutation.mutate(proxyLink.trim());
  };

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const handleSavePaymentCard = () => toast.success("اطلاعات کارت ذخیره شد");
  const handleSaveCommission = () => toast.success("تنظیمات کمیسیون ذخیره شد");
  const handleSavePricing = () => toast.success("تنظیمات قیمت‌گذاری ذخیره شد");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin" className="p-2 rounded-lg hover:bg-accent transition-colors">
          <ArrowRight className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">تنظیمات</h1>
          <p className="text-muted mt-1">تنظیمات پلتفرم و سیستم</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ============ V2Ray Proxy Settings ============ */}
        <Card className="lg:col-span-2 border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-primary" />
              پروکسی V2Ray (تلگرام)
              {proxyStatus?.enabled && (
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full mr-2",
                  proxyStatus.connected ? "bg-success-light text-success" : "bg-warning-light text-warning"
                )}>
                  {proxyStatus.connected ? "متصل" : "قطع"}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted">
              چون سرور در ایران قرار دارد و تلگرام فیلتر است، لینک V2Ray وارد کنید تا ربات از طریق آن متصل شود.
            </p>

            {/* Current Status */}
            {proxyStatus?.enabled && (
              <div className={cn(
                "p-4 rounded-xl border",
                proxyStatus.connected ? "bg-success-light/50 border-success/30" : "bg-warning-light/50 border-warning/30"
              )}>
                <div className="flex items-center gap-3">
                  {proxyStatus.connected ? (
                    <Wifi className="w-5 h-5 text-success" />
                  ) : (
                    <WifiOff className="w-5 h-5 text-warning" />
                  )}
                  <div>
                    <p className="font-medium text-foreground">
                      {proxyStatus.connected ? "پروکسی متصل است" : "پروکسی ذخیره شده ولی اتصال تأیید نشده"}
                    </p>
                    <p className="text-xs text-muted mt-0.5">
                      پروتکل: <span className="font-mono">{proxyStatus.protocol}</span>
                      {" | "}
                      سرور: <span className="font-mono">{proxyStatus.server}</span>
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Link Input */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">لینک V2Ray</label>
              <textarea
                className="w-full px-4 py-3 border border-border rounded-lg text-sm font-mono focus:ring-2 focus:ring-primary focus:border-primary min-h-[80px] resize-y"
                dir="ltr"
                placeholder="vmess://... یا vless://... یا trojan://... یا ss://..."
                value={proxyLink}
                onChange={(e) => { setProxyLink(e.target.value); setTestResult(null); }}
              />
            </div>

            {/* Test Result */}
            {testResult && (
              <div className={cn(
                "p-3 rounded-lg border flex items-center gap-3",
                testResult.success ? "bg-success-light/50 border-success/30" : "bg-destructive/10 border-destructive/30"
              )}>
                {testResult.success ? (
                  <Zap className="w-5 h-5 text-success flex-shrink-0" />
                ) : (
                  <WifiOff className="w-5 h-5 text-destructive flex-shrink-0" />
                )}
                <div>
                  <p className={cn("text-sm font-medium", testResult.success ? "text-success" : "text-destructive")}>
                    {testResult.success ? `اتصال موفق (${testResult.latency_ms}ms)` : "اتصال ناموفق"}
                  </p>
                  <p className="text-xs text-muted">{testResult.message}</p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="primary"
                onClick={handleSaveProxy}
                disabled={!proxyLink.trim() || saveProxyMutation.isPending}
                isLoading={saveProxyMutation.isPending}
                leftIcon={<Save className="w-4 h-4" />}
              >
                ذخیره لینک
              </Button>

              <Button
                variant="outline"
                onClick={handleTestProxy}
                disabled={!proxyStatus?.enabled || isTesting}
                isLoading={isTesting}
                leftIcon={<Activity className="w-4 h-4" />}
              >
                تست اتصال
              </Button>

              <Button
                variant="outline"
                onClick={() => restartMutation.mutate()}
                disabled={!proxyStatus?.enabled || restartMutation.isPending}
                isLoading={restartMutation.isPending}
                leftIcon={<RefreshCw className="w-4 h-4" />}
              >
                اعمال و ری‌استارت ربات
              </Button>

              {proxyStatus?.enabled && (
                <Button
                  variant="ghost"
                  onClick={() => {
                    if (confirm("آیا مطمئنید؟ پروکسی حذف و ربات مستقیم متصل خواهد شد.")) {
                      removeProxyMutation.mutate();
                    }
                  }}
                  disabled={removeProxyMutation.isPending}
                  className="text-destructive hover:text-destructive"
                  leftIcon={<Trash2 className="w-4 h-4" />}
                >
                  حذف پروکسی
                </Button>
              )}
            </div>

            <div className="p-3 bg-accent rounded-lg text-xs text-muted space-y-1">
              <p><strong>راهنما:</strong></p>
              <p>۱. لینک V2Ray را از سرویس‌دهنده VPN کپی و اینجا پیست کنید</p>
              <p>۲. «ذخیره لینک» را بزنید تا تنظیمات ذخیره شود</p>
              <p>۳. «تست اتصال» را بزنید تا اتصال به تلگرام بررسی شود</p>
              <p>۴. اگر اتصال موفق بود، «اعمال و ری‌استارت ربات» را بزنید</p>
            </div>
          </CardContent>
        </Card>

        {/* Payment Card Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-primary" />
              اطلاعات کارت پرداخت
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted">
              این اطلاعات برای پرداخت‌های کارت به کارت به کاربران نمایش داده می‌شود.
            </p>
            <Input label="شماره کارت" value={cardNumber} onChange={(e) => setCardNumber(e.target.value)} placeholder="۶۰۳۷-XXXX-XXXX-XXXX" dir="ltr" />
            <Input label="نام صاحب کارت" value={cardHolder} onChange={(e) => setCardHolder(e.target.value)} placeholder="نام و نام خانوادگی" />
            <Button variant="primary" onClick={handleSavePaymentCard} leftIcon={<Save className="w-4 h-4" />}>ذخیره تغییرات</Button>
          </CardContent>
        </Card>

        {/* Commission Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Percent className="w-5 h-5 text-success" />
              نرخ کمیسیون
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted">درصد کمیسیون پلتفرم که از مبلغ چاپخانه کسر می‌شود.</p>
            <div className="flex items-center gap-3">
              <Input type="number" value={commissionRate} onChange={(e) => setCommissionRate(e.target.value)} className="w-24" min="0" max="100" />
              <span className="text-lg font-medium">درصد</span>
            </div>
            <div className="p-3 bg-accent rounded-lg text-sm">
              <p className="text-muted">
                با نرخ فعلی، برای هر ۱,۰۰۰,۰۰۰ تومان سفارش،
                <span className="font-bold text-foreground mx-1">
                  {toPersianNumber((1000000 * parseInt(commissionRate || "0") / 100).toLocaleString())}
                </span>
                تومان کمیسیون دریافت می‌شود.
              </p>
            </div>
            <Button variant="primary" onClick={handleSaveCommission} leftIcon={<Save className="w-4 h-4" />}>ذخیره تغییرات</Button>
          </CardContent>
        </Card>

        {/* Pricing Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-warning" />
              قیمت‌گذاری خدمات
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted">تعرفه خدمات اعتبارسنجی و اصلاح طرح.</p>
            <Input label="هزینه اعتبارسنجی (تومان)" type="number" value={validationPrice} onChange={(e) => setValidationPrice(e.target.value)} placeholder="50000" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="حداقل هزینه اصلاح" type="number" defaultValue="100000" placeholder="100000" />
              <Input label="حداکثر هزینه اصلاح" type="number" defaultValue="600000" placeholder="600000" />
            </div>
            <Button variant="primary" onClick={handleSavePricing} leftIcon={<Save className="w-4 h-4" />}>ذخیره تغییرات</Button>
          </CardContent>
        </Card>

        {/* Notifications Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-info" />
              تنظیمات اعلان‌ها
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted">تنظیم نحوه ارسال اعلان‌ها به کاربران و مدیران.</p>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 bg-accent rounded-lg cursor-pointer">
                <span>اعلان سفارش جدید به چاپخانه</span>
                <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
              </label>
              <label className="flex items-center justify-between p-3 bg-accent rounded-lg cursor-pointer">
                <span>اعلان پرداخت جدید به ادمین</span>
                <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
              </label>
              <label className="flex items-center justify-between p-3 bg-accent rounded-lg cursor-pointer">
                <span>اعلان وضعیت سفارش به مشتری</span>
                <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
              </label>
            </div>
            <Button variant="primary" leftIcon={<Save className="w-4 h-4" />}>ذخیره تغییرات</Button>
          </CardContent>
        </Card>

        {/* System Info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              اطلاعات سیستم
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 bg-accent rounded-xl text-center">
                <p className="text-sm text-muted">نسخه API</p>
                <p className="text-lg font-bold">v1.0.0</p>
              </div>
              <div className="p-4 bg-accent rounded-xl text-center">
                <p className="text-sm text-muted">نسخه فرانت‌اند</p>
                <p className="text-lg font-bold">v1.0.0</p>
              </div>
              <div className="p-4 bg-accent rounded-xl text-center">
                <p className="text-sm text-muted">دیتابیس</p>
                <p className="text-lg font-bold">PostgreSQL</p>
              </div>
              <div className="p-4 bg-accent rounded-xl text-center">
                <p className="text-sm text-muted">وضعیت</p>
                <p className="text-lg font-bold text-success">آنلاین</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
