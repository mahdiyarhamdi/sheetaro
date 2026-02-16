"use client";

import Link from "next/link";
import Image from "next/image";
import { Phone, Mail, MapPin, Send } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-surface border-t border-border mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand section */}
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Image
                src="/images/logo.svg"
                alt="Sheetaro"
                width={40}
                height={40}
                className="rounded-lg"
              />
              <span className="text-xl font-bold text-primary">شیتارو</span>
            </Link>
            <p className="text-sm text-muted leading-relaxed">
              سامانه آنلاین طراحی و چاپ لیبل و فاکتور با کیفیت بالا و قیمت مناسب
            </p>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">دسترسی سریع</h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/new-order"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  ثبت سفارش
                </Link>
              </li>
              <li>
                <Link
                  href="/orders"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  پیگیری سفارش
                </Link>
              </li>
              <li>
                <Link
                  href="/pricing"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  تعرفه‌ها
                </Link>
              </li>
              <li>
                <Link
                  href="/faq"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  سوالات متداول
                </Link>
              </li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">خدمات</h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/services/label"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  طراحی لیبل
                </Link>
              </li>
              <li>
                <Link
                  href="/services/invoice"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  طراحی فاکتور
                </Link>
              </li>
              <li>
                <Link
                  href="/services/printing"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  چاپ اختصاصی
                </Link>
              </li>
              <li>
                <Link
                  href="/services/consulting"
                  className="text-sm text-muted hover:text-primary transition-colors"
                >
                  مشاوره رایگان
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">تماس با ما</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2 text-sm text-muted">
                <Phone className="w-4 h-4 text-primary" />
                <span dir="ltr">۰۲۱-۱۲۳۴۵۶۷۸</span>
              </li>
              <li className="flex items-center gap-2 text-sm text-muted">
                <Mail className="w-4 h-4 text-primary" />
                <span>info@sheetaro.com</span>
              </li>
              <li className="flex items-start gap-2 text-sm text-muted">
                <MapPin className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                <span>تهران، خیابان ولیعصر</span>
              </li>
              <li className="flex items-center gap-2 text-sm text-muted">
                <Send className="w-4 h-4 text-primary" />
                <a
                  href="https://t.me/sheetarobot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  @sheetarobot
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted">
            © {currentYear} شیتارو. تمامی حقوق محفوظ است.
          </p>
          <div className="flex items-center gap-4">
            <Link
              href="/terms"
              className="text-sm text-muted hover:text-primary transition-colors"
            >
              قوانین و مقررات
            </Link>
            <Link
              href="/privacy"
              className="text-sm text-muted hover:text-primary transition-colors"
            >
              حریم خصوصی
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

