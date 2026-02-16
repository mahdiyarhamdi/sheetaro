"use client";

import { useState } from "react";
import { Header, Footer } from "@/components/layout";
import { ChevronDown } from "lucide-react";

const faqs = [
  { q: "شیتارو چیست؟", a: "شیتارو یک پلتفرم آنلاین طراحی و چاپ لیبل و فاکتور است. شما می‌توانید به صورت آنلاین سفارش دهید، با طراحان حرفه‌ای ارتباط بگیرید و محصول نهایی را درب منزل تحویل بگیرید." },
  { q: "مدت زمان تحویل سفارش چقدر است؟", a: "بسته به نوع سفارش و پلن انتخابی، معمولاً بین ۳ تا ۵ روز کاری طول می‌کشد. پلن خصوصی اولویت بالاتری در صف چاپ دارد." },
  { q: "آیا می‌توانم طرح خودم را آپلود کنم؟", a: "بله! اگر فایل طراحی آماده دارید (PDF, AI, PSD, EPS, SVG, PNG, JPG) می‌توانید آن را آپلود کنید و فقط هزینه چاپ پرداخت کنید." },
  { q: "اعتبارسنجی فنی چیست؟", a: "تیم فنی ما قبل از ارسال طرح به چاپخانه، رزولوشن، رنگ‌بندی (CMYK)، حاشیه‌های امن و سایر استانداردهای چاپ را بررسی می‌کند تا از کیفیت نهایی اطمینان حاصل شود." },
  { q: "چند بار می‌توانم طرح را ویرایش کنم؟", a: "در پلن نیمه‌خصوصی ۳ بار ریویژن رایگان دارید. در پلن خصوصی ریویژن نامحدود (تا ۱۴ روز) خواهید داشت. در پلن عمومی امکان ویرایش قالب وجود دارد." },
  { q: "نحوه پرداخت چگونه است؟", a: "پرداخت به صورت کارت به کارت انجام می‌شود. پس از واریز مبلغ، تصویر رسید را آپلود کنید و پس از تأیید ادمین، سفارش شما پردازش می‌شود." },
  { q: "آیا امکان لغو سفارش وجود دارد؟", a: "بله، تا قبل از شروع طراحی می‌توانید سفارش را لغو کنید و وجه به حسابتان بازگردانده می‌شود. پس از شروع طراحی، شرایط بازگشت وجه متفاوت خواهد بود." },
  { q: "آیا ارسال به تمام نقاط ایران انجام می‌شود؟", a: "بله، ارسال به تمام نقاط ایران از طریق پست پیشتاز انجام می‌شود و کد رهگیری برای شما ارسال خواهد شد." },
];

export default function FAQPage() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-16 lg:py-24 bg-surface">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="text-center mb-16">
            <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
              سوالات <span className="text-primary">متداول</span>
            </h1>
            <p className="text-lg text-muted">پاسخ سوالات رایج درباره خدمات شیتارو</p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-white rounded-xl border border-border/50 overflow-hidden">
                <button
                  onClick={() => setOpen(open === i ? null : i)}
                  className="w-full flex items-center justify-between p-5 text-right hover:bg-surface/50 transition-colors"
                >
                  <span className="font-semibold text-foreground">{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 text-muted shrink-0 mr-4 transition-transform ${open === i ? "rotate-180" : ""}`} />
                </button>
                {open === i && (
                  <div className="px-5 pb-5 text-sm text-muted leading-relaxed border-t border-border/30 pt-4">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-12 text-center bg-white rounded-2xl p-8 border border-border/50">
            <h3 className="text-lg font-bold text-foreground mb-2">سوال دیگری دارید؟</h3>
            <p className="text-muted mb-4">از طریق ربات تلگرام یا پشتیبانی با ما در ارتباط باشید.</p>
            <a href="https://t.me/sheetarobot" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 bg-primary text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors">
              پشتیبانی تلگرام
            </a>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
