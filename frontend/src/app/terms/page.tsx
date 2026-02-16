import { Header, Footer } from "@/components/layout";

export default function TermsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-16 lg:py-24 bg-surface">
        <div className="container mx-auto px-4 max-w-3xl">
          <h1 className="text-3xl lg:text-4xl font-black text-foreground mb-8 text-center">قوانین و مقررات</h1>

          <div className="bg-white rounded-2xl p-8 border border-border/50 prose prose-sm max-w-none space-y-6">
            <section>
              <h2 className="text-lg font-bold text-foreground">۱. شرایط عمومی</h2>
              <p className="text-muted leading-relaxed">
                با استفاده از خدمات شیتارو، شما شرایط و قوانین زیر را می‌پذیرید. این قوانین ممکن است در آینده به‌روزرسانی شوند و ادامه استفاده از خدمات به معنای پذیرش تغییرات است.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۲. ثبت‌نام و حساب کاربری</h2>
              <p className="text-muted leading-relaxed">
                کاربران موظفند اطلاعات صحیح و معتبر هنگام ثبت‌نام ارائه دهند. هر شخص تنها مجاز به داشتن یک حساب کاربری است. مسئولیت حفظ امنیت حساب بر عهده کاربر است.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۳. سفارش‌ها و پرداخت</h2>
              <p className="text-muted leading-relaxed">
                پس از ثبت سفارش و تأیید پرداخت، فرآیند طراحی و چاپ آغاز می‌شود. قیمت‌ها بر اساس نوع خدمت، تعداد و مشخصات فنی محاسبه می‌شود. پرداخت به صورت کارت به کارت انجام می‌شود.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۴. لغو و بازگشت وجه</h2>
              <p className="text-muted leading-relaxed">
                لغو سفارش قبل از شروع فرآیند طراحی با بازگشت کامل وجه امکان‌پذیر است. پس از شروع طراحی، بخشی از مبلغ بابت خدمات انجام‌شده کسر خواهد شد. در صورت عدم رضایت از کیفیت چاپ، امکان چاپ مجدد یا بازگشت وجه وجود دارد.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۵. مالکیت معنوی</h2>
              <p className="text-muted leading-relaxed">
                طرح‌های سفارشی پس از تأیید نهایی و پرداخت کامل، متعلق به سفارش‌دهنده خواهد بود. قالب‌های عمومی شیتارو متعلق به شرکت بوده و فقط حق استفاده اعطا می‌شود.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۶. مسئولیت محتوا</h2>
              <p className="text-muted leading-relaxed">
                مسئولیت محتوای درج‌شده در طرح‌ها (متن، تصاویر، لوگو) بر عهده سفارش‌دهنده است. شیتارو مسئولیتی در قبال صحت اطلاعات ارائه‌شده توسط کاربر ندارد.
              </p>
            </section>

            <section>
              <h2 className="text-lg font-bold text-foreground">۷. حل اختلاف</h2>
              <p className="text-muted leading-relaxed">
                در صورت بروز اختلاف، ابتدا از طریق مذاکره و پشتیبانی شیتارو اقدام به حل مسئله خواهد شد. مرجع نهایی حل اختلاف، مراجع قضایی ذی‌صلاح کشور ایران خواهد بود.
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
