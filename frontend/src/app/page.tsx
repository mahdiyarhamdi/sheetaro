"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
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
  Layers,
  Printer,
  Clock,
  Award,
  Sparkles,
  ChevronDown,
  Eye,
  PenTool,
  FileCheck,
  Truck,
  MessageCircle,
  Crown,
  BarChart3,
  Quote,
} from "lucide-react";
import { cn, toPersianNumber } from "@/lib/utils";

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

  /* pricing plans */
  const plans = [
    {
      name: "عمومی",
      nameEn: "Public",
      price: "رایگان",
      priceNote: "فقط هزینه چاپ",
      icon: Layers,
      color: "text-info",
      bgColor: "bg-info/10",
      borderColor: "border-info/20",
      features: [
        "انتخاب از قالب‌های آماده",
        "جایگذاری لوگو و اطلاعات",
        "پیش‌نمایش آنلاین",
        "دانلود فایل نهایی",
      ],
      popular: false,
    },
    {
      name: "نیمه‌خصوصی",
      nameEn: "Semi-Private",
      price: "از ۶۰۰,۰۰۰",
      priceNote: "تومان + هزینه چاپ",
      icon: PenTool,
      color: "text-primary",
      bgColor: "bg-primary/10",
      borderColor: "border-primary/30",
      features: [
        "طراحی اختصاصی توسط طراح حرفه‌ای",
        "پرسشنامه طراحی",
        "۳ بار ریویژن رایگان",
        "اعتبارسنجی فنی فایل",
        "چت مستقیم با طراح",
      ],
      popular: true,
    },
    {
      name: "خصوصی",
      nameEn: "Private",
      price: "۵,۰۰۰,۰۰۰",
      priceNote: "تومان + هزینه چاپ",
      icon: Crown,
      color: "text-warning",
      bgColor: "bg-warning/10",
      borderColor: "border-warning/30",
      features: [
        "طراحی کاملاً اختصاصی",
        "ریویژن نامحدود (۱۴ روز)",
        "طراح اختصاصی ویژه",
        "اولویت در صف چاپ",
        "پشتیبانی ویژه",
      ],
      popular: false,
    },
  ];

  /* testimonials */
  const testimonials = [
    {
      name: "سارا محمدی",
      role: "صاحب برند آرایشی",
      rating: 5,
      text: "لیبل‌های شیتارو کیفیت فوق‌العاده‌ای دارن. طراحشون خیلی حرفه‌ای بود و دقیقاً چیزی که می‌خواستم رو طراحی کرد.",
      avatar: "س",
    },
    {
      name: "علی رضایی",
      role: "تولیدکننده مواد غذایی",
      rating: 5,
      text: "سرعت کارشون عالیه. از ثبت سفارش تا دریافت لیبل‌ها فقط ۳ روز طول کشید. قطعاً دوباره سفارش می‌دم.",
      avatar: "ع",
    },
    {
      name: "مریم حسینی",
      role: "فروشگاه آنلاین",
      rating: 5,
      text: "فاکتورهای طراحی‌شده خیلی حرفه‌ای هستن و به برندمون اعتبار بیشتری دادن. ممنون از تیم شیتارو.",
      avatar: "م",
    },
  ];

  /* workflow steps */
  const workflowSteps = [
    {
      icon: Package,
      title: "انتخاب محصول و پلن",
      description: "از کاتالوگ محصولات، نوع لیبل یا فاکتور و پلن طراحی مناسب خود را انتخاب کنید.",
      color: "from-blue-500 to-blue-600",
    },
    {
      icon: PenTool,
      title: "طراحی اختصاصی",
      description: "طراح حرفه‌ای ما بر اساس اطلاعات و سلیقه شما، طرح منحصربفرد ایجاد می‌کند.",
      color: "from-purple-500 to-purple-600",
    },
    {
      icon: FileCheck,
      title: "تایید و اعتبارسنجی",
      description: "طرح نهایی را بررسی و تایید کنید. تیم فنی ما کیفیت چاپ را اعتبارسنجی می‌کند.",
      color: "from-amber-500 to-amber-600",
    },
    {
      icon: Printer,
      title: "چاپ حرفه‌ای",
      description: "سفارش شما در بهترین چاپخانه‌های شبکه ما با بالاترین کیفیت چاپ می‌شود.",
      color: "from-emerald-500 to-emerald-600",
    },
    {
      icon: Truck,
      title: "ارسال سریع",
      description: "محصول نهایی بسته‌بندی و به آدرس شما ارسال می‌شود. پیگیری آنلاین تا لحظه تحویل.",
      color: "from-rose-500 to-rose-600",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* ═══════════ HERO ═══════════ */}
        <section className="relative overflow-hidden py-20 lg:py-32">
          {/* background */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#f0faf3] via-background to-white" />
          <div className="absolute top-[-20%] right-[-10%] w-[700px] h-[700px] bg-primary/[0.04] rounded-full blur-3xl" />
          <div className="absolute bottom-[-15%] left-[-10%] w-[500px] h-[500px] bg-emerald-400/[0.04] rounded-full blur-3xl" />

          <div className="container mx-auto px-4 relative">
            {/* centered layout */}
            <div className="max-w-4xl mx-auto text-center">
              {/* badge */}
              <div className="inline-flex items-center gap-2 bg-primary/10 text-primary text-sm font-medium px-5 py-2 rounded-full mb-8">
                <Zap className="w-4 h-4" />
                سریع، آنلاین، حرفه‌ای
              </div>

              {/* heading */}
              <h1 className="text-4xl md:text-5xl lg:text-[3.5rem] font-black text-foreground mb-6 leading-[1.35] tracking-tight">
                طراحی و چاپ آنلاین
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-l from-primary to-emerald-500">
                  با تیم حرفه‌ای شیتارو
                </span>
              </h1>

              <p className="text-lg lg:text-xl text-muted leading-relaxed mb-10 max-w-2xl mx-auto">
                ایده‌تان را بگویید، ما طراحی و چاپ می‌کنیم. سفارش آنلاین، ارتباط مستقیم با طراح، اعتبارسنجی فنی و ارسال سریع — همه در یک پلتفرم.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row items-center gap-4 justify-center mb-12">
                <Link href={isLoggedIn ? "/new-order" : "/register"}>
                  <Button variant="primary" size="lg" className="text-base px-10 py-3.5 h-auto shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all" rightIcon={<ArrowLeft className="w-5 h-5" />}>
                    {isLoggedIn ? "ثبت سفارش جدید" : "شروع رایگان"}
                  </Button>
                </Link>
                <a href="https://t.me/sheetarobot" target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="lg" className="text-base px-10 py-3.5 h-auto" leftIcon={<Send className="w-5 h-5" />}>
                    ربات تلگرام
                  </Button>
                </a>
              </div>

              {/* hero feature pills */}
              <div className="flex flex-wrap items-center justify-center gap-3 mb-14">
                {[
                  { icon: PenTool, text: "طراحی اختصاصی" },
                  { icon: Printer, text: "چاپ حرفه‌ای" },
                  { icon: FileCheck, text: "اعتبارسنجی فنی" },
                  { icon: Truck, text: "ارسال سریع" },
                  { icon: MessageCircle, text: "چت با طراح" },
                ].map((pill, i) => (
                  <div key={i} className="flex items-center gap-2 bg-white border border-border/60 rounded-full px-4 py-2 text-sm text-foreground shadow-sm">
                    <pill.icon className="w-4 h-4 text-primary" />
                    {pill.text}
                  </div>
                ))}
              </div>

              {/* social proof row */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-10">
                <div className="flex items-center gap-3">
                  <div className="flex -space-x-2 space-x-reverse">
                    {["س", "ع", "م", "ر"].map((l, i) => (
                      <div key={i} className={cn("w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-[10px] font-bold text-white", i === 0 ? "bg-primary" : i === 1 ? "bg-emerald-500" : i === 2 ? "bg-blue-500" : "bg-amber-500")}>
                        {l}
                      </div>
                    ))}
                  </div>
                  <div className="text-sm text-right">
                    <div className="flex items-center gap-0.5">
                      {[1, 2, 3, 4, 5].map((s) => (
                        <Star key={s} className="w-3 h-3 fill-warning text-warning" />
                      ))}
                      <span className="font-bold text-foreground mr-1 text-xs">۴.۸</span>
                    </div>
                    <p className="text-muted text-xs">+۱۰۰۰ مشتری راضی</p>
                  </div>
                </div>

                <div className="hidden sm:block w-px h-8 bg-border/60" />

                <div className="flex items-center gap-2 text-sm text-muted">
                  <Shield className="w-4 h-4 text-success" />
                  <span>تضمین کیفیت و بازگشت وجه</span>
                </div>

                <div className="hidden sm:block w-px h-8 bg-border/60" />

                <div className="flex items-center gap-2 text-sm text-muted">
                  <Clock className="w-4 h-4 text-blue-500" />
                  <span>تحویل ۳ تا ۵ روزه</span>
                </div>
              </div>
            </div>
          </div>

          {/* scroll hint */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 animate-bounce hidden lg:block">
            <ChevronDown className="w-6 h-6 text-muted/40" />
          </div>
        </section>

        {/* ═══════════ FEATURES (Why Sheetaro) ═══════════ */}
        <section className="py-20 lg:py-28 bg-surface">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <span className="text-sm font-semibold text-primary bg-primary/10 px-4 py-1.5 rounded-full">مزایای شیتارو</span>
              <h2 className="text-3xl lg:text-4xl font-bold text-foreground mt-4 mb-4">
                چرا هزاران کسب‌وکار <span className="text-primary">شیتارو</span> را انتخاب کرده‌اند؟
              </h2>
              <p className="text-muted max-w-2xl mx-auto text-lg">
                ترکیب فناوری، هنر و سرعت — تجربه‌ای متفاوت در طراحی و چاپ
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
              {[
                { icon: Palette, title: "طراحی اختصاصی", desc: "تیم طراحان حرفه‌ای ما طرحی منحصربفرد و متناسب با هویت برند شما خلق می‌کنند.", color: "from-violet-500 to-purple-600" },
                { icon: Eye, title: "پیش‌نمایش آنلاین", desc: "قبل از چاپ، طرح نهایی را آنلاین ببینید و هر تغییری که می‌خواهید اعمال کنید.", color: "from-blue-500 to-cyan-500" },
                { icon: FileCheck, title: "اعتبارسنجی فنی", desc: "تیم فنی ما رزولوشن، رنگ‌بندی و استانداردهای چاپ را قبل از ارسال به چاپخانه بررسی می‌کند.", color: "from-amber-500 to-orange-500" },
                { icon: Printer, title: "شبکه چاپخانه‌ها", desc: "سفارش شما در بهترین چاپخانه شبکه ما، با تجهیزات مدرن و متریال باکیفیت چاپ می‌شود.", color: "from-emerald-500 to-green-600" },
                { icon: MessageCircle, title: "ارتباط مستقیم", desc: "از طریق چت داخلی مستقیماً با طراح خود در ارتباط باشید و بازخورد بدهید.", color: "from-pink-500 to-rose-500" },
                { icon: BarChart3, title: "پیگیری لحظه‌ای", desc: "وضعیت سفارش خود را از لحظه ثبت تا تحویل درب منزل به صورت آنلاین پیگیری کنید.", color: "from-teal-500 to-emerald-500" },
              ].map((f, i) => (
                <div key={i} className="group bg-white rounded-2xl p-6 lg:p-8 border border-border/50 hover:border-primary/20 hover:shadow-lg transition-all duration-300">
                  <div className={cn("w-14 h-14 rounded-2xl bg-gradient-to-br flex items-center justify-center mb-5 group-hover:scale-110 transition-transform", f.color)}>
                    <f.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-2">{f.title}</h3>
                  <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════ HOW IT WORKS ═══════════ */}
        <section className="py-20 lg:py-28 bg-gradient-to-b from-background to-surface">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <span className="text-sm font-semibold text-primary bg-primary/10 px-4 py-1.5 rounded-full">مراحل سفارش</span>
              <h2 className="text-3xl lg:text-4xl font-bold text-foreground mt-4 mb-4">
                از سفارش تا تحویل، در <span className="text-primary">۵ قدم ساده</span>
              </h2>
              <p className="text-muted max-w-2xl mx-auto text-lg">
                فرایند ساده و شفاف — شما فقط سفارش دهید، بقیه‌اش با ماست
              </p>
            </div>

            <div className="relative max-w-4xl mx-auto">
              {/* vertical line */}
              <div className="absolute right-6 lg:right-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary/20 via-primary/40 to-primary/20 hidden md:block" />

              <div className="space-y-8 lg:space-y-12">
                {workflowSteps.map((step, i) => (
                  <div key={i} className={cn("relative flex items-start gap-6 lg:gap-12", i % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse")}>
                    {/* number circle */}
                    <div className="absolute right-0 lg:right-auto lg:left-1/2 lg:-translate-x-1/2 z-10">
                      <div className={cn("w-12 h-12 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-lg shadow-lg", step.color)}>
                        {toPersianNumber(i + 1)}
                      </div>
                    </div>

                    {/* card */}
                    <div className={cn("mr-16 lg:mr-0 lg:w-[calc(50%-3rem)] bg-white rounded-2xl p-6 border border-border/50 hover:shadow-md transition-shadow", i % 2 === 0 ? "lg:text-right" : "lg:mr-auto lg:text-right")}>
                      <div className={cn("w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center mb-3", step.color)}>
                        <step.icon className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-lg font-bold text-foreground mb-2">{step.title}</h3>
                      <p className="text-sm text-muted leading-relaxed">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════ PRICING ═══════════ */}
        <section className="py-20 lg:py-28 bg-surface">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <span className="text-sm font-semibold text-primary bg-primary/10 px-4 py-1.5 rounded-full">تعرفه‌ها</span>
              <h2 className="text-3xl lg:text-4xl font-bold text-foreground mt-4 mb-4">
                پلن مناسب <span className="text-primary">کسب‌وکار خود</span> را انتخاب کنید
              </h2>
              <p className="text-muted max-w-2xl mx-auto text-lg">
                با هر بودجه‌ای می‌توانید از خدمات شیتارو بهره‌مند شوید
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
              {plans.map((plan, i) => (
                <div key={i} className={cn("relative bg-white rounded-2xl p-6 lg:p-8 border transition-all hover:shadow-lg", plan.popular ? "border-primary shadow-md scale-[1.02] lg:scale-105" : "border-border/50")}>
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="bg-primary text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-lg shadow-primary/25">
                        محبوب‌ترین
                      </span>
                    </div>
                  )}

                  <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center mb-4", plan.bgColor)}>
                    <plan.icon className={cn("w-6 h-6", plan.color)} />
                  </div>

                  <h3 className="text-xl font-bold text-foreground mb-1">{plan.name}</h3>
                  <p className="text-xs text-muted mb-4">{plan.nameEn}</p>

                  <div className="mb-6">
                    <span className="text-2xl lg:text-3xl font-black text-foreground">{plan.price}</span>
                    <span className="text-sm text-muted block mt-1">{plan.priceNote}</span>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((f, j) => (
                      <li key={j} className="flex items-start gap-2 text-sm">
                        <CheckCircle className={cn("w-4 h-4 shrink-0 mt-0.5", plan.color)} />
                        <span className="text-foreground">{f}</span>
                      </li>
                    ))}
                  </ul>

                  <Link href={isLoggedIn ? "/new-order" : "/register"} className="block">
                    <Button variant={plan.popular ? "primary" : "outline"} className="w-full" size="lg">
                      {isLoggedIn ? "ثبت سفارش" : "شروع کنید"}
                    </Button>
                  </Link>
                </div>
              ))}
            </div>

            <p className="text-center text-sm text-muted mt-8">
              همچنین می‌توانید <span className="font-semibold text-foreground">طرح خودتان</span> را آپلود کنید و فقط هزینه چاپ پرداخت کنید.
            </p>
          </div>
        </section>

        {/* ═══════════ TESTIMONIALS ═══════════ */}
        <section className="py-20 lg:py-28 bg-gradient-to-b from-background to-primary-50/30">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <span className="text-sm font-semibold text-primary bg-primary/10 px-4 py-1.5 rounded-full">نظرات مشتریان</span>
              <h2 className="text-3xl lg:text-4xl font-bold text-foreground mt-4 mb-4">
                مشتریان ما <span className="text-primary">چه می‌گویند؟</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
              {testimonials.map((t, i) => (
                <div key={i} className="bg-white rounded-2xl p-6 lg:p-8 border border-border/50 hover:shadow-md transition-shadow relative">
                  <Quote className="w-10 h-10 text-primary/10 absolute top-4 left-4" />
                  <div className="flex items-center gap-1 mb-4">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star key={s} className={cn("w-4 h-4", s <= t.rating ? "fill-warning text-warning" : "text-gray-200")} />
                    ))}
                  </div>
                  <p className="text-sm text-foreground leading-relaxed mb-6">«{t.text}»</p>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                      {t.avatar}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-foreground">{t.name}</p>
                      <p className="text-xs text-muted">{t.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════ FINAL CTA ═══════════ */}
        <section className="relative py-20 lg:py-28 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary to-emerald-600" />
          <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle, white 1px, transparent 1px)", backgroundSize: "24px 24px" }} />

          <div className="container mx-auto px-4 text-center relative">
            <div className="max-w-2xl mx-auto">
              <div className="inline-flex items-center gap-2 bg-white/15 text-white text-sm font-medium px-4 py-2 rounded-full mb-6 backdrop-blur-sm">
                <Sparkles className="w-4 h-4" />
                همین حالا شروع کنید
              </div>

              <h2 className="text-3xl lg:text-5xl font-black text-white mb-6 leading-tight">
                {isLoggedIn ? "سفارش بعدی‌تان را ثبت کنید" : "هویت بصری برندتان را بسازید"}
              </h2>
              <p className="text-white/80 text-lg mb-10 max-w-lg mx-auto leading-relaxed">
                {isLoggedIn
                  ? "طراحان ما آماده خلق طرح‌های جدید برای کسب‌وکار شما هستند."
                  : "ثبت‌نام رایگان است. در کمتر از ۳۰ ثانیه حساب خود را بسازید و اولین سفارش را ثبت کنید."}
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href={isLoggedIn ? "/new-order" : "/register"}>
                  <Button variant="secondary" size="lg" className="bg-white text-primary hover:bg-primary-50 text-base px-8 py-3 h-auto shadow-lg" rightIcon={<ArrowLeft className="w-5 h-5" />}>
                    {isLoggedIn ? "ثبت سفارش جدید" : "ثبت‌نام رایگان"}
                  </Button>
                </Link>
                <a href="https://t.me/sheetarobot" target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="lg" className="border-white/30 text-white hover:bg-white/10 text-base px-8 py-3 h-auto" leftIcon={<Send className="w-5 h-5" />}>
                    ربات تلگرام
                  </Button>
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════ TRUST BADGES ═══════════ */}
        <section className="py-10 bg-white border-t border-border/50">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap items-center justify-center gap-8 lg:gap-16">
              {[
                { icon: Shield, label: "پرداخت امن", sub: "کارت به کارت مطمئن" },
                { icon: Clock, label: "پشتیبانی ۲۴/۷", sub: "تلگرام و چت آنلاین" },
                { icon: Award, label: "تضمین کیفیت", sub: "اعتبارسنجی فنی قبل از چاپ" },
                { icon: Truck, label: "ارسال سراسری", sub: "تحویل ۳ تا ۵ روزه" },
              ].map((badge, i) => (
                <div key={i} className="flex items-center gap-3 text-center">
                  <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center">
                    <badge.icon className="w-5 h-5 text-primary" />
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-foreground">{badge.label}</p>
                    <p className="text-xs text-muted">{badge.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
