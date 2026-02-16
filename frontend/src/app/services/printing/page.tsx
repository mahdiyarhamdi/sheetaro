import Link from "next/link";
import { Header, Footer } from "@/components/layout";
import { Button } from "@/components/ui";
import { CheckCircle, ArrowLeft, Printer, Award, Clock, Shield } from "lucide-react";

export default function PrintingServicePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="py-16 lg:py-24 bg-gradient-to-b from-emerald-50/50 to-background">
          <div className="container mx-auto px-4 max-w-4xl">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Printer className="w-8 h-8 text-emerald-600" />
              </div>
              <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
                <span className="text-emerald-600">چاپ اختصاصی</span> حرفه‌ای
              </h1>
              <p className="text-lg text-muted max-w-2xl mx-auto">
                شبکه چاپخانه‌های مجهز شیتارو، با تجهیزات مدرن و متریال باکیفیت در خدمت شماست.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {[
                { icon: Printer, title: "تجهیزات مدرن", desc: "چاپخانه‌های شبکه ما با جدیدترین دستگاه‌های چاپ دیجیتال و افست مجهز هستند." },
                { icon: Award, title: "کنترل کیفیت", desc: "هر سفارش قبل از ارسال از نظر کیفیت چاپ، رنگ و برش کنترل می‌شود." },
                { icon: Clock, title: "تحویل سریع", desc: "سفارش‌های فوری در ۲۴ ساعت و عادی در ۳ تا ۵ روز کاری آماده می‌شوند." },
                { icon: Shield, title: "تضمین کیفیت", desc: "اگر از کیفیت چاپ رضایت نداشتید، سفارش مجدداً چاپ یا هزینه بازگردانده می‌شود." },
              ].map((item, i) => (
                <div key={i} className="bg-white rounded-xl p-6 border border-border/50">
                  <item.icon className="w-8 h-8 text-emerald-600 mb-3" />
                  <h3 className="font-bold text-foreground mb-2">{item.title}</h3>
                  <p className="text-sm text-muted">{item.desc}</p>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-2xl p-8 border border-border/50 mb-8">
              <h3 className="text-xl font-bold text-foreground mb-4">امکانات چاپ</h3>
              <ul className="grid md:grid-cols-2 gap-3">
                {["چاپ دیجیتال", "چاپ افست", "چاپ روی کاغذ گلاسه", "چاپ روی کاغذ کرافت", "لمینت براق و مات", "طلاکوب و نقره‌کوب", "برش دای‌کات اختصاصی", "چاپ UV"].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="text-center">
              <Link href="/new-order">
                <Button variant="primary" size="lg" rightIcon={<ArrowLeft className="w-5 h-5" />}>ثبت سفارش چاپ</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
