import Link from "next/link";
import { Header, Footer } from "@/components/layout";
import { Button } from "@/components/ui";
import { CheckCircle, Layers, PenTool, Crown, ArrowLeft } from "lucide-react";

export default function PricingPage() {
  const plans = [
    {
      name: "عمومی",
      nameEn: "Public",
      price: "رایگان",
      priceNote: "فقط هزینه چاپ",
      icon: Layers,
      color: "text-info",
      bgColor: "bg-info/10",
      features: [
        "انتخاب از قالب‌های آماده",
        "جایگذاری لوگو و اطلاعات",
        "پیش‌نمایش آنلاین",
        "دانلود فایل نهایی",
        "پشتیبانی از طریق تلگرام",
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
      features: [
        "طراحی اختصاصی توسط طراح حرفه‌ای",
        "پرسشنامه طراحی هوشمند",
        "۳ بار ریویژن رایگان",
        "اعتبارسنجی فنی فایل",
        "چت مستقیم با طراح",
        "پشتیبانی اختصاصی",
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
      features: [
        "طراحی کاملاً اختصاصی",
        "ریویژن نامحدود (۱۴ روز)",
        "طراح اختصاصی ویژه",
        "اولویت در صف چاپ",
        "پشتیبانی VIP",
        "مشاوره برندینگ رایگان",
      ],
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-16 lg:py-24 bg-surface">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
              تعرفه‌ها و <span className="text-primary">پلن‌های طراحی</span>
            </h1>
            <p className="text-lg text-muted max-w-2xl mx-auto">
              با هر بودجه‌ای می‌توانید از خدمات شیتارو بهره‌مند شوید. پلن مناسب خود را انتخاب کنید.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
            {plans.map((plan, i) => (
              <div key={i} className={`relative bg-white rounded-2xl p-8 border transition-all hover:shadow-lg ${plan.popular ? "border-primary shadow-md scale-[1.02]" : "border-border/50"}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-primary text-white text-xs font-bold px-4 py-1.5 rounded-full">محبوب‌ترین</span>
                  </div>
                )}
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${plan.bgColor}`}>
                  <plan.icon className={`w-7 h-7 ${plan.color}`} />
                </div>
                <h3 className="text-xl font-bold text-foreground">{plan.name}</h3>
                <p className="text-xs text-muted mb-4">{plan.nameEn}</p>
                <div className="mb-6">
                  <span className="text-3xl font-black text-foreground">{plan.price}</span>
                  <span className="text-sm text-muted block mt-1">{plan.priceNote}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm">
                      <CheckCircle className={`w-4 h-4 shrink-0 mt-0.5 ${plan.color}`} />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/register" className="block">
                  <Button variant={plan.popular ? "primary" : "outline"} className="w-full" size="lg">شروع کنید</Button>
                </Link>
              </div>
            ))}
          </div>

          <div className="max-w-3xl mx-auto bg-white rounded-2xl p-8 border border-border/50 text-center">
            <h3 className="text-xl font-bold text-foreground mb-3">طرح خودتان را دارید؟</h3>
            <p className="text-muted mb-6">اگر فایل طراحی آماده دارید، می‌توانید آن را آپلود کنید و فقط هزینه چاپ را پرداخت کنید.</p>
            <Link href="/new-order">
              <Button variant="primary" rightIcon={<ArrowLeft className="w-4 h-4" />}>ثبت سفارش با طرح خودم</Button>
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
