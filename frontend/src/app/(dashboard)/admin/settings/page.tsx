"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
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
  Shield,
  Database,
} from "lucide-react";
import toast from "react-hot-toast";
import { toPersianNumber } from "@/lib/utils";

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

  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const handleSavePaymentCard = () => {
    toast.success("اطلاعات کارت ذخیره شد");
  };

  const handleSaveCommission = () => {
    toast.success("تنظیمات کمیسیون ذخیره شد");
  };

  const handleSavePricing = () => {
    toast.success("تنظیمات قیمت‌گذاری ذخیره شد");
  };

  const settingSections = [
    {
      title: "اطلاعات کارت پرداخت",
      description: "شماره کارت برای دریافت پرداخت‌های کارت به کارت",
      icon: CreditCard,
      color: "bg-primary-50 text-primary",
    },
    {
      title: "نرخ کمیسیون",
      description: "درصد کمیسیون پلتفرم از چاپخانه‌ها",
      icon: Percent,
      color: "bg-success-light text-success",
    },
    {
      title: "قیمت‌گذاری خدمات",
      description: "قیمت خدمات اعتبارسنجی و اصلاح",
      icon: Settings,
      color: "bg-warning-light text-warning",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/admin"
          className="p-2 rounded-lg hover:bg-accent transition-colors"
        >
          <ArrowRight className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">تنظیمات</h1>
          <p className="text-muted mt-1">تنظیمات پلتفرم و سیستم</p>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
            <Input
              label="شماره کارت"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              placeholder="۶۰۳۷-XXXX-XXXX-XXXX"
              dir="ltr"
            />
            <Input
              label="نام صاحب کارت"
              value={cardHolder}
              onChange={(e) => setCardHolder(e.target.value)}
              placeholder="نام و نام خانوادگی"
            />
            <Button
              variant="primary"
              onClick={handleSavePaymentCard}
              leftIcon={<Save className="w-4 h-4" />}
            >
              ذخیره تغییرات
            </Button>
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
            <p className="text-sm text-muted">
              درصد کمیسیون پلتفرم که از مبلغ چاپخانه کسر می‌شود. تسویه هفتگی انجام می‌شود.
            </p>
            <div className="flex items-center gap-3">
              <Input
                type="number"
                value={commissionRate}
                onChange={(e) => setCommissionRate(e.target.value)}
                className="w-24"
                min="0"
                max="100"
              />
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
            <Button
              variant="primary"
              onClick={handleSaveCommission}
              leftIcon={<Save className="w-4 h-4" />}
            >
              ذخیره تغییرات
            </Button>
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
            <p className="text-sm text-muted">
              تعرفه خدمات اعتبارسنجی و اصلاح طرح.
            </p>
            <Input
              label="هزینه اعتبارسنجی (تومان)"
              type="number"
              value={validationPrice}
              onChange={(e) => setValidationPrice(e.target.value)}
              placeholder="50000"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="حداقل هزینه اصلاح"
                type="number"
                defaultValue="100000"
                placeholder="100000"
              />
              <Input
                label="حداکثر هزینه اصلاح"
                type="number"
                defaultValue="600000"
                placeholder="600000"
              />
            </div>
            <Button
              variant="primary"
              onClick={handleSavePricing}
              leftIcon={<Save className="w-4 h-4" />}
            >
              ذخیره تغییرات
            </Button>
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
            <p className="text-sm text-muted">
              تنظیم نحوه ارسال اعلان‌ها به کاربران و مدیران.
            </p>
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
            <Button
              variant="primary"
              leftIcon={<Save className="w-4 h-4" />}
            >
              ذخیره تغییرات
            </Button>
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

