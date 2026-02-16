"use client";

import { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import { profileApi, authApi } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Input,
  Textarea,
  Badge,
} from "@/components/ui";
import {
  User,
  Phone,
  MapPin,
  Send,
  Edit2,
  CheckCircle,
  XCircle,
  Save,
  X,
  Hash,
  Copy,
  ExternalLink,
  RefreshCw,
} from "lucide-react";
import { formatDate, toPersianNumber } from "@/lib/utils";
import toast from "react-hot-toast";

const profileSchema = z.object({
  full_name: z.string().min(2, "نام باید حداقل ۲ کاراکتر باشد"),
  city: z.string().optional(),
  address: z.string().optional(),
  postal_code: z.string().optional(),
  bio: z
    .string()
    .max(500, "بیوگرافی نباید بیشتر از ۵۰۰ کاراکتر باشد")
    .optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const BOT_USERNAME = "sheetarobot";

export default function ProfilePage() {
  const { user, refetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Telegram link OTP state
  const [otpCode, setOtpCode] = useState<string | null>(null);
  const [otpExpiry, setOtpExpiry] = useState<Date | null>(null);
  const [otpCountdown, setOtpCountdown] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);

  // Countdown timer
  useEffect(() => {
    if (!otpExpiry) return;
    const tick = () => {
      const remaining = Math.max(
        0,
        Math.floor((otpExpiry.getTime() - Date.now()) / 1000)
      );
      setOtpCountdown(remaining);
      if (remaining <= 0) {
        setOtpCode(null);
        setOtpExpiry(null);
      }
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [otpExpiry]);

  const generateOtp = useCallback(async () => {
    setIsGenerating(true);
    try {
      const { data } = await authApi.generateTelegramLink();
      setOtpCode(data.otp);
      setOtpExpiry(new Date(data.expires_at));
      toast.success("کد اتصال ایجاد شد");
    } catch {
      toast.error("خطا در ایجاد کد اتصال");
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const copyOtp = useCallback(() => {
    if (otpCode) {
      navigator.clipboard.writeText(otpCode);
      toast.success("کد کپی شد");
    }
  }, [otpCode]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || "",
      city: user?.city || "",
      address: user?.address || "",
      postal_code: user?.postal_code || "",
      bio: user?.bio || "",
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        full_name: user.full_name || "",
        city: user.city || "",
        address: user.address || "",
        postal_code: user.postal_code || "",
        bio: user.bio || "",
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: ProfileFormData) => {
    setIsSaving(true);
    try {
      await profileApi.update(data);
      toast.success("پروفایل با موفقیت به‌روزرسانی شد");
      setIsEditing(false);
      refetchUser();
    } catch {
      toast.error("خطا در به‌روزرسانی پروفایل");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    reset({
      full_name: user?.full_name || "",
      city: user?.city || "",
      address: user?.address || "",
      postal_code: user?.postal_code || "",
      bio: user?.bio || "",
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">پروفایل من</h1>
          <p className="text-muted mt-1">مدیریت اطلاعات حساب کاربری</p>
        </div>
        {!isEditing && (
          <Button
            variant="outline"
            leftIcon={<Edit2 className="w-4 h-4" />}
            onClick={() => setIsEditing(true)}
          >
            ویرایش
          </Button>
        )}
      </div>

      {/* Profile card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
              <User className="w-8 h-8 text-primary" />
            </div>
            <div>
              <CardTitle>{user?.full_name || user?.first_name}</CardTitle>
              <p className="text-sm text-muted">
                عضویت از {user?.created_at ? formatDate(user.created_at) : "-"}
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {isEditing ? (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label="نام و نام خانوادگی"
                leftIcon={<User className="w-4 h-4" />}
                error={errors.full_name?.message}
                {...register("full_name")}
              />

              <Input
                label="شهر"
                leftIcon={<MapPin className="w-4 h-4" />}
                placeholder="مثال: تهران"
                {...register("city")}
              />

              <Textarea
                label="آدرس"
                placeholder="آدرس کامل خود را وارد کنید"
                {...register("address")}
              />

              <Input
                label="کد پستی"
                leftIcon={<Hash className="w-4 h-4" />}
                placeholder="مثال: ۱۲۳۴۵۶۷۸۹۰"
                {...register("postal_code")}
              />

              <Textarea
                label="درباره من"
                placeholder="چند خط درباره خود یا کسب‌وکارتان بنویسید"
                {...register("bio")}
              />

              <div className="flex items-center gap-3 pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  isLoading={isSaving}
                  leftIcon={<Save className="w-4 h-4" />}
                >
                  ذخیره تغییرات
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  leftIcon={<X className="w-4 h-4" />}
                >
                  انصراف
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              {/* Phone */}
              <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
                <Phone className="w-5 h-5 text-muted" />
                <div>
                  <p className="text-sm text-muted">شماره موبایل</p>
                  <p className="font-medium" dir="ltr">
                    {user?.phone_number || "-"}
                  </p>
                </div>
                <Badge variant="success" size="sm" className="mr-auto">
                  <CheckCircle className="w-3 h-3 ml-1" />
                  تأیید شده
                </Badge>
              </div>

              {/* Telegram -- inline connection */}
              {user?.telegram_id ? (
                <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
                  <Send className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-sm text-muted">تلگرام</p>
                    <p className="font-medium">
                      {toPersianNumber(user.telegram_id)}
                    </p>
                  </div>
                  <Badge variant="success" size="sm" className="mr-auto">
                    <CheckCircle className="w-3 h-3 ml-1" />
                    متصل
                  </Badge>
                </div>
              ) : (
                <div className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl space-y-3">
                  <div className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
                    <Send className="w-5 h-5" />
                    <span className="font-semibold">اتصال تلگرام</span>
                  </div>
                  <p className="text-sm text-blue-600 dark:text-blue-300">
                    با اتصال تلگرام، نوتیفیکیشن‌های سفارشات خود را دریافت
                    کنید.
                  </p>

                  {otpCode && otpCountdown > 0 ? (
                    <>
                      {/* OTP display */}
                      <div className="flex items-center gap-2">
                        <div
                          className="flex-1 text-center font-mono text-2xl tracking-[0.4em] bg-white dark:bg-gray-900 border border-blue-200 dark:border-blue-700 rounded-lg py-2 select-all cursor-pointer"
                          onClick={copyOtp}
                        >
                          {otpCode}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={copyOtp}
                          leftIcon={<Copy className="w-4 h-4" />}
                        >
                          کپی
                        </Button>
                      </div>
                      <p className="text-xs text-blue-500 text-center">
                        انقضا در {toPersianNumber(Math.floor(otpCountdown / 60))}:
                        {toPersianNumber(
                          String(otpCountdown % 60).padStart(2, "0")
                        )}{" "}
                        دقیقه
                      </p>

                      {/* Steps */}
                      <ol className="text-xs text-muted space-y-1 list-decimal list-inside pr-1">
                        <li>روی دکمه «رفتن به ربات» کلیک کنید</li>
                        <li>
                          دستور <code>/linkweb</code> را بزنید
                        </li>
                        <li>کد بالا را وارد کنید</li>
                      </ol>

                      <a
                        href={`https://t.me/${BOT_USERNAME}?start=linkweb`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block"
                      >
                        <Button
                          variant="primary"
                          className="w-full"
                          leftIcon={<ExternalLink className="w-4 h-4" />}
                        >
                          رفتن به ربات تلگرام
                        </Button>
                      </a>
                    </>
                  ) : (
                    <Button
                      variant="primary"
                      className="w-full"
                      onClick={generateOtp}
                      isLoading={isGenerating}
                      leftIcon={<RefreshCw className="w-4 h-4" />}
                    >
                      ایجاد کد اتصال
                    </Button>
                  )}
                </div>
              )}

              {/* City */}
              <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
                <MapPin className="w-5 h-5 text-muted" />
                <div>
                  <p className="text-sm text-muted">شهر</p>
                  <p className="font-medium">{user?.city || "—"}</p>
                </div>
              </div>

              {/* Address */}
              <div className="flex items-start gap-3 p-3 bg-accent rounded-lg">
                <MapPin className="w-5 h-5 text-muted shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-muted">آدرس</p>
                  <p className="font-medium">{user?.address || "—"}</p>
                </div>
              </div>

              {/* Postal Code */}
              <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
                <Hash className="w-5 h-5 text-muted" />
                <div>
                  <p className="text-sm text-muted">کد پستی</p>
                  <p className="font-medium">{user?.postal_code || "—"}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Account info */}
      <Card>
        <CardHeader>
          <CardTitle>اطلاعات حساب</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-muted">نوع حساب</span>
              <Badge variant={user?.is_admin ? "info" : "default"}>
                {user?.is_admin ? "مدیر" : "کاربر عادی"}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-muted">وضعیت حساب</span>
              <Badge variant="success">
                <CheckCircle className="w-3 h-3 ml-1" />
                فعال
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-muted">اتصال تلگرام</span>
              {user?.telegram_id ? (
                <Badge variant="success">
                  <CheckCircle className="w-3 h-3 ml-1" />
                  متصل
                </Badge>
              ) : (
                <Badge variant="outline">
                  <XCircle className="w-3 h-3 ml-1" />
                  متصل نشده
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Card className="border-danger/30">
        <CardHeader>
          <CardTitle className="text-danger">منطقه خطر</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted mb-4">
            با حذف حساب کاربری، تمام اطلاعات و سفارشات شما به طور دائمی حذف
            خواهد شد.
          </p>
          <Button
            variant="outline"
            className="text-danger border-danger hover:bg-danger-light"
          >
            حذف حساب کاربری
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
