import Link from "next/link";
import { Header, Footer } from "@/components/layout";
import { Button } from "@/components/ui";
import { CheckCircle, ArrowLeft, Palette, FileCheck, Printer, Truck } from "lucide-react";

export default function LabelServicePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="py-16 lg:py-24 bg-gradient-to-b from-primary/5 to-background">
          <div className="container mx-auto px-4 max-w-4xl">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Palette className="w-8 h-8 text-primary" />
              </div>
              <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
                طراحی و چاپ <span className="text-primary">لیبل</span>
              </h1>
              <p className="text-lg text-muted max-w-2xl mx-auto">
                لیبل حرفه‌ای و باکیفیت برای محصولات شما. از طراحی اختصاصی تا چاپ و ارسال.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {[
                { icon: Palette, title: "طراحی اختصاصی", desc: "طراحان حرفه‌ای ما با توجه به هویت برند شما، لیبل منحصربفردی طراحی می‌کنند." },
                { icon: FileCheck, title: "اعتبارسنجی فنی", desc: "قبل از چاپ، تمام استانداردهای فنی بررسی می‌شود تا کیفیت نهایی تضمین شود." },
                { icon: Printer, title: "چاپ باکیفیت", desc: "با بهترین متریال و تجهیزات مدرن، لیبل‌های شما با کیفیت عالی چاپ می‌شوند." },
                { icon: Truck, title: "ارسال سریع", desc: "سفارش شما در ۳ تا ۵ روز کاری آماده و به آدرستان ارسال می‌شود." },
              ].map((item, i) => (
                <div key={i} className="bg-white rounded-xl p-6 border border-border/50">
                  <item.icon className="w-8 h-8 text-primary mb-3" />
                  <h3 className="font-bold text-foreground mb-2">{item.title}</h3>
                  <p className="text-sm text-muted">{item.desc}</p>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-2xl p-8 border border-border/50 mb-8">
              <h3 className="text-xl font-bold text-foreground mb-4">انواع لیبل‌های قابل سفارش</h3>
              <ul className="grid md:grid-cols-2 gap-3">
                {["لیبل محصولات غذایی", "لیبل محصولات آرایشی و بهداشتی", "لیبل شیشه و بطری", "لیبل بسته‌بندی", "لیبل دارویی", "لیبل صنعتی", "لیبل لوازم خانگی", "لیبل پوشاک و منسوجات"].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-primary shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="text-center">
              <Link href="/new-order">
                <Button variant="primary" size="lg" rightIcon={<ArrowLeft className="w-5 h-5" />}>ثبت سفارش لیبل</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
