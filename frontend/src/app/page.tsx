"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui";
import { Header, Footer } from "@/components/layout";
import {
  CheckCircle,
  Zap,
  Shield,
  Palette,
  ArrowLeft,
  Package,
  Star,
  Send,
} from "lucide-react";

// Check if user is logged in
function useIsLoggedIn() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);
  }, []);
  
  return isLoggedIn;
}

export default function HomePage() {
  const isLoggedIn = useIsLoggedIn();
  const features = [
    {
      icon: Palette,
      title: "طراحی اختصاصی",
      description: "طراحی منحصر به فرد برای برند شما توسط تیم حرفه‌ای",
    },
    {
      icon: Zap,
      title: "سرعت بالا",
      description: "تحویل سریع سفارشات در کمترین زمان ممکن",
    },
    {
      icon: Shield,
      title: "کیفیت تضمینی",
      description: "استفاده از بهترین متریال‌ها و تکنولوژی‌های روز",
    },
    {
      icon: Package,
      title: "تنوع محصولات",
      description: "انواع لیبل و فاکتور با طرح‌های متنوع",
    },
  ];

  const steps = [
    {
      number: "۱",
      title: "انتخاب محصول",
      description: "محصول مورد نظر خود را از کاتالوگ انتخاب کنید",
    },
    {
      number: "۲",
      title: "سفارشی‌سازی",
      description: "مشخصات و اطلاعات طراحی را وارد کنید",
    },
    {
      number: "۳",
      title: "پرداخت",
      description: "هزینه را از طریق کارت به کارت پرداخت کنید",
    },
    {
      number: "۴",
      title: "دریافت طرح",
      description: "طرح نهایی را دریافت و استفاده کنید",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header - uses shared component with auth state */}
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-background to-primary-100 py-16 lg:py-24">
          <div className="container mx-auto px-4">
            <div className="flex flex-col lg:flex-row items-center gap-12">
              <div className="flex-1 text-center lg:text-right">
                <h1 className="text-3xl lg:text-5xl font-bold text-foreground mb-6 leading-tight">
                  طراحی و چاپ حرفه‌ای
                  <br />
                  <span className="text-primary">لیبل و فاکتور</span>
                </h1>
                <p className="text-lg text-muted mb-8 max-w-lg mx-auto lg:mx-0">
                  با شیتارو، طرح‌های اختصاصی و باکیفیت برای کسب‌وکار خود سفارش دهید.
                  سریع، آسان و با قیمت مناسب.
                </p>
                <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                  <Link href={isLoggedIn ? "/new-order" : "/register"}>
                    <Button
                      variant="primary"
                      size="lg"
                      rightIcon={<ArrowLeft className="w-5 h-5" />}
                    >
                      {isLoggedIn ? "سفارش جدید" : "شروع کنید"}
                    </Button>
                  </Link>
                  {isLoggedIn ? (
                    <Link href="/orders">
                      <Button variant="outline" size="lg">
                        سفارشات من
                      </Button>
                    </Link>
                  ) : (
                    <Link href="/pricing">
                      <Button variant="outline" size="lg">
                        مشاهده تعرفه‌ها
                      </Button>
                    </Link>
                  )}
                </div>

                {/* Stats */}
                <div className="flex items-center justify-center lg:justify-start gap-8 mt-10">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">+۱۰۰۰</p>
                    <p className="text-sm text-muted">مشتری راضی</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">+۵۰۰۰</p>
                    <p className="text-sm text-muted">سفارش انجام شده</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">۴.۸</p>
                    <p className="text-sm text-muted flex items-center gap-1">
                      <Star className="w-3 h-3 fill-warning text-warning" />
                      امتیاز
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex-1 max-w-md lg:max-w-none">
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/20 rounded-3xl blur-3xl" />
                  <Image
                    src="/images/logo.png"
                    alt="Hero"
                    width={500}
                    height={500}
                    className="relative rounded-3xl shadow-strong mx-auto"
                    priority
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 lg:py-24 bg-surface">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-2xl lg:text-3xl font-bold text-foreground mb-4">
                چرا شیتارو؟
              </h2>
              <p className="text-muted max-w-2xl mx-auto">
                ما با تمرکز بر کیفیت و رضایت مشتری، بهترین خدمات طراحی و چاپ را
                ارائه می‌دهیم
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-background rounded-xl p-6 text-center hover:shadow-medium transition-shadow"
                >
                  <div className="w-14 h-14 rounded-xl bg-primary-50 flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it works */}
        <section className="py-16 lg:py-24 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-2xl lg:text-3xl font-bold text-foreground mb-4">
                مراحل ثبت سفارش
              </h2>
              <p className="text-muted max-w-2xl mx-auto">
                در چند قدم ساده سفارش خود را ثبت کنید
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {steps.map((step, index) => (
                <div key={index} className="relative">
                  <div className="bg-surface rounded-xl p-6 text-center border border-border h-full">
                    <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                      {step.number}
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      {step.title}
                    </h3>
                    <p className="text-sm text-muted">{step.description}</p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -left-4 transform -translate-y-1/2">
                      <ArrowLeft className="w-6 h-6 text-primary/30" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 lg:py-24 bg-primary">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-2xl lg:text-3xl font-bold text-white mb-4">
              {isLoggedIn ? "سفارش جدید ثبت کنید" : "آماده شروع هستید؟"}
            </h2>
            <p className="text-primary-100 mb-8 max-w-lg mx-auto">
              {isLoggedIn 
                ? "طرح‌های اختصاصی برای کسب‌وکار شما آماده است. همین حالا سفارش دهید."
                : "همین حالا ثبت‌نام کنید و اولین سفارش خود را ثبت کنید. تیم ما آماده کمک به شماست."}
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href={isLoggedIn ? "/new-order" : "/register"}>
                <Button
                  variant="secondary"
                  size="lg"
                  className="bg-white text-primary hover:bg-primary-50"
                >
                  {isLoggedIn ? "سفارش جدید" : "ثبت‌نام رایگان"}
                </Button>
              </Link>
              <a
                href="https://t.me/sheetaro_bot"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button
                  variant="outline"
                  size="lg"
                  leftIcon={<Send className="w-5 h-5" />}
                  className="border-white text-white hover:bg-white/10"
                >
                  ربات تلگرام
                </Button>
              </a>
            </div>
          </div>
        </section>

        {/* Trust badges */}
        <section className="py-12 bg-surface border-t border-border">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap items-center justify-center gap-6 lg:gap-12">
              <div className="flex items-center gap-2 text-muted">
                <CheckCircle className="w-5 h-5 text-success" />
                <span className="text-sm">پرداخت امن</span>
              </div>
              <div className="flex items-center gap-2 text-muted">
                <CheckCircle className="w-5 h-5 text-success" />
                <span className="text-sm">پشتیبانی ۲۴/۷</span>
              </div>
              <div className="flex items-center gap-2 text-muted">
                <CheckCircle className="w-5 h-5 text-success" />
                <span className="text-sm">تضمین کیفیت</span>
              </div>
              <div className="flex items-center gap-2 text-muted">
                <CheckCircle className="w-5 h-5 text-success" />
                <span className="text-sm">تحویل سریع</span>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
