"use client";

import Link from "next/link";
import Image from "next/image";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
}

export function AuthLayout({ children, title, description }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-background to-primary-100 flex flex-col">
      {/* Header */}
      <header className="p-4">
        <Link href="/" className="flex items-center gap-2 w-fit">
          <Image
            src="/images/logo.svg"
            alt="Sheetaro"
            width={40}
            height={40}
            className="rounded-lg"
          />
          <span className="text-xl font-bold text-primary">شیتارو</span>
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Card */}
          <div className="bg-surface rounded-2xl shadow-medium p-6 sm:p-8 animate-slide-up">
            {/* Header */}
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-foreground mb-2">
                {title}
              </h1>
              {description && (
                <p className="text-muted text-sm">{description}</p>
              )}
            </div>

            {/* Content */}
            {children}
          </div>

          {/* Footer links */}
          <div className="mt-6 text-center text-sm text-muted">
            <Link href="/terms" className="hover:text-primary transition-colors">
              قوانین و مقررات
            </Link>
            <span className="mx-2">•</span>
            <Link href="/privacy" className="hover:text-primary transition-colors">
              حریم خصوصی
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-4 text-center">
        <p className="text-sm text-muted">
          © {new Date().getFullYear()} شیتارو. تمامی حقوق محفوظ است.
        </p>
      </footer>
    </div>
  );
}

