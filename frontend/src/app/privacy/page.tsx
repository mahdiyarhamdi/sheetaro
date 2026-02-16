import { Header, Footer } from "@/components/layout";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-16 lg:py-24 bg-surface">
        <div className="container mx-auto px-4 max-w-3xl">
          <h1 className="text-3xl lg:text-4xl font-black text-foreground mb-8 text-center">حریم خصوصی</h1>

          <div className="bg-white rounded-2xl p-8 border border-border/50 prose prose-sm max-w-none space-y-6">
            <section>
              <h2 className="text-lg font-bold text-foreground">۱. جمع‌آوری اطلاعات</h2>
              <p className="text-muted leading-relaxed">
                شیتارو اطلاعات شخصی شما شامل نام، شماره تلفن و آدرس را فقط برای ارائه خدمات و ارسال سفارشات جمع‌آوری می‌کند. اطلاعات پرداخت به صورت امن پردازش می‌شود.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۲. استفاده از اطلاعات</h2>
              <p className="text-muted leading-relaxed">
                اطلاعات شما فقط برای پردازش سفارشات، ارسال اطلاع‌رسانی‌های مرتبط و بهبود خدمات استفاده می‌شود. هیچ‌گاه اطلاعات شخصی شما به اشخاص ثالث فروخته یا واگذار نخواهد شد.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۳. امنیت داده‌ها</h2>
              <p className="text-muted leading-relaxed">
                ما از روش‌های استاندارد صنعتی برای محافظت از اطلاعات شما استفاده می‌کنیم. ارتباطات از طریق SSL رمزنگاری می‌شوند و دسترسی به داده‌ها محدود به افراد مجاز است.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۴. کوکی‌ها</h2>
              <p className="text-muted leading-relaxed">
                وب‌سایت ما از کوکی‌ها برای بهبود تجربه کاربری و ذخیره تنظیمات شما استفاده می‌کند. می‌توانید کوکی‌ها را در تنظیمات مرورگر خود غیرفعال کنید.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۵. حقوق کاربران</h2>
              <p className="text-muted leading-relaxed">
                شما حق دسترسی، اصلاح و حذف اطلاعات شخصی خود را دارید. برای درخواست تغییر یا حذف اطلاعات، از طریق پشتیبانی با ما تماس بگیرید.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۶. تغییرات</h2>
              <p className="text-muted leading-relaxed">
                این سیاست ممکن است به‌روزرسانی شود. تغییرات مهم از طریق پیامک یا ایمیل اطلاع‌رسانی خواهد شد. ادامه استفاده از خدمات به معنای پذیرش تغییرات است.
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
