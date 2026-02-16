import { Header, Footer } from "@/components/layout";
import { MessageCircle, Phone, Send, Clock } from "lucide-react";

export default function ConsultingServicePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="py-16 lg:py-24 bg-gradient-to-b from-purple-50/50 to-background">
          <div className="container mx-auto px-4 max-w-4xl">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <MessageCircle className="w-8 h-8 text-purple-600" />
              </div>
              <h1 className="text-3xl lg:text-5xl font-black text-foreground mb-4">
                <span className="text-purple-600">مشاوره رایگان</span> طراحی و چاپ
              </h1>
              <p className="text-lg text-muted max-w-2xl mx-auto">
                تیم متخصص شیتارو آماده پاسخگویی به سوالات و راهنمایی شما در انتخاب بهترین گزینه‌هاست.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
              {[
                { icon: MessageCircle, title: "مشاوره طراحی", desc: "راهنمایی در انتخاب سبک طراحی، رنگ‌بندی و المان‌های بصری متناسب با برند شما." },
                { icon: Phone, title: "مشاوره چاپ", desc: "راهنمایی در انتخاب بهترین نوع کاغذ، روکش و تکنیک چاپ برای محصول شما." },
                { icon: Send, title: "مشاوره آنلاین", desc: "از طریق ربات تلگرام یا چت داخلی سوالات خود را بپرسید و سریع پاسخ بگیرید." },
                { icon: Clock, title: "پاسخگویی سریع", desc: "تیم پشتیبانی ما در ساعات کاری آماده پاسخگویی به سوالات شماست." },
              ].map((item, i) => (
                <div key={i} className="bg-white rounded-xl p-6 border border-border/50">
                  <item.icon className="w-8 h-8 text-purple-600 mb-3" />
                  <h3 className="font-bold text-foreground mb-2">{item.title}</h3>
                  <p className="text-sm text-muted">{item.desc}</p>
                </div>
              ))}
            </div>

            <div className="text-center bg-white rounded-2xl p-8 border border-border/50">
              <h3 className="text-xl font-bold text-foreground mb-4">راه‌های ارتباطی</h3>
              <div className="flex flex-wrap justify-center gap-4">
                <a href="https://t.me/sheetarobot" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                  <Send className="w-5 h-5" /> ربات تلگرام
                </a>
                <a href="tel:02112345678" className="inline-flex items-center gap-2 bg-white text-foreground border border-border px-6 py-3 rounded-lg font-medium hover:bg-surface transition-colors">
                  <Phone className="w-5 h-5" /> تماس تلفنی
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
