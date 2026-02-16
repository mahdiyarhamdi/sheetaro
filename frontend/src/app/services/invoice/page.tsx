import Link from "next/link";
import { Header, Footer } from "@/components/layout";
import { Button } from "@/components/ui";
import { CheckCircle, ArrowLeft, FileText, Shield, Zap, Layers } from "lucide-react";

export default function InvoiceServicePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="py-16 lg:py-24 bg-gradient-to-b from-blue-50/50 to-background">
          <div className="container mx-auto px-4 max-w-4xl">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
                طراحی و چاپ <span className="text-blue-600">فاکتور</span>
              </h1>
              <p className="text-lg text-muted max-w-2xl mx-auto">
                فاکتور حرفه‌ای، اعتبار بیشتر برای کسب‌وکار شما. طراحی اختصاصی متناسب با برندتان.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {[
                { icon: Layers, title: "قالب‌های متنوع", desc: "ده‌ها قالب آماده فاکتور با امکان سفارشی‌سازی کامل." },
                { icon: Shield, title: "استاندارد مالیاتی", desc: "فاکتورها مطابق استانداردهای سازمان مالیاتی طراحی می‌شوند." },
                { icon: Zap, title: "طراحی سریع", desc: "فاکتور شما در کمترین زمان ممکن طراحی و آماده چاپ می‌شود." },
                { icon: FileText, title: "فرمت‌های مختلف", desc: "فاکتور A4, A5, سه‌نسخه‌ای و تک‌نسخه‌ای با کاغذ کاربن‌لس." },
              ].map((item, i) => (
                <div key={i} className="bg-white rounded-xl p-6 border border-border/50">
                  <item.icon className="w-8 h-8 text-blue-600 mb-3" />
                  <h3 className="font-bold text-foreground mb-2">{item.title}</h3>
                  <p className="text-sm text-muted">{item.desc}</p>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-2xl p-8 border border-border/50 mb-8">
              <h3 className="text-xl font-bold text-foreground mb-4">انواع فاکتور قابل سفارش</h3>
              <ul className="grid md:grid-cols-2 gap-3">
                {["فاکتور رسمی فروش", "فاکتور خدمات", "پیش‌فاکتور", "فاکتور سه‌نسخه‌ای", "رسید پرداخت", "قبض انبار"].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="text-center">
              <Link href="/new-order">
                <Button variant="primary" size="lg" rightIcon={<ArrowLeft className="w-5 h-5" />}>ثبت سفارش فاکتور</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
