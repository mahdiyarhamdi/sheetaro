"use client";

import { Send, Phone, Mail, Clock, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui";

export default function SupportPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">پشتیبانی</h1>
        <p className="text-muted mt-1">در صورت نیاز به راهنمایی، از طریق روش‌های زیر با ما در ارتباط باشید.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-border/50">
          <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
            <Send className="w-6 h-6 text-primary" />
          </div>
          <h3 className="font-bold text-foreground mb-2">ربات تلگرام</h3>
          <p className="text-sm text-muted mb-4">سریع‌ترین راه ارتباط با ما. ۲۴ ساعته فعال.</p>
          <a href="https://t.me/sheetarobot" target="_blank" rel="noopener noreferrer">
            <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>شروع گفتگو</Button>
          </a>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-border/50">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
            <Phone className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-bold text-foreground mb-2">تماس تلفنی</h3>
          <p className="text-sm text-muted mb-4">در ساعات کاری (۹ تا ۱۸) پاسخگوی شما هستیم.</p>
          <a href="tel:02112345678">
            <Button variant="outline" leftIcon={<Phone className="w-4 h-4" />}>۰۲۱-۱۲۳۴۵۶۷۸</Button>
          </a>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-border/50">
          <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
            <Mail className="w-6 h-6 text-emerald-600" />
          </div>
          <h3 className="font-bold text-foreground mb-2">ایمیل</h3>
          <p className="text-sm text-muted mb-4">برای مکاتبات رسمی و ارسال مستندات.</p>
          <a href="mailto:info@sheetaro.com">
            <Button variant="outline" leftIcon={<Mail className="w-4 h-4" />}>info@sheetaro.com</Button>
          </a>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-border/50">
          <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4">
            <Clock className="w-6 h-6 text-amber-600" />
          </div>
          <h3 className="font-bold text-foreground mb-2">ساعات کاری</h3>
          <p className="text-sm text-muted mb-2">شنبه تا پنج‌شنبه: ۹ صبح تا ۶ عصر</p>
          <p className="text-sm text-muted">ربات تلگرام: ۲۴ ساعته</p>
        </div>
      </div>

      <div className="bg-primary/5 rounded-2xl p-6 border border-primary/10">
        <div className="flex items-start gap-4">
          <MessageCircle className="w-8 h-8 text-primary shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-foreground mb-1">سوالات متداول</h3>
            <p className="text-sm text-muted mb-3">قبل از تماس، شاید پاسخ سوال شما در بخش سوالات متداول باشد.</p>
            <a href="/faq" className="text-primary text-sm font-medium hover:underline">مشاهده سوالات متداول ←</a>
          </div>
        </div>
      </div>
    </div>
  );
}
