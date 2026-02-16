import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";

export const metadata: Metadata = {
  title: "شیتارو | طراحی و چاپ لیبل و فاکتور",
  description:
    "سامانه آنلاین طراحی و چاپ لیبل و فاکتور با کیفیت بالا و قیمت مناسب",
  keywords: ["لیبل", "فاکتور", "طراحی", "چاپ", "شیتارو"],
  authors: [{ name: "Sheetaro Team" }],
  openGraph: {
    title: "شیتارو | طراحی و چاپ لیبل و فاکتور",
    description:
      "سامانه آنلاین طراحی و چاپ لیبل و فاکتور با کیفیت بالا و قیمت مناسب",
    type: "website",
    locale: "fa_IR",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <head>
        <meta name="theme-color" content="#16a34a" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="شیتارو" />
      </head>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
