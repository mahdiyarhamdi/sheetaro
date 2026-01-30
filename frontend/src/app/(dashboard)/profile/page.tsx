"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
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
} from "lucide-react";
import { formatDate, toPersianNumber } from "@/lib/utils";
import toast from "react-hot-toast";

const profileSchema = z.object({
  full_name: z.string().min(2, "نام باید حداقل ۲ کاراکتر باشد"),
  city: z.string().optional(),
  address: z.string().optional(),
  bio: z.string().max(500, "بیوگرافی نباید بیشتر از ۵۰۰ کاراکتر باشد").optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export default function ProfilePage() {
  const { user, refetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || "",
      city: "",
      address: "",
      bio: "",
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setIsSaving(true);
    try {
      // TODO: Call API to update profile
      // await api.patch("/users/me", data);
      toast.success("پروفایل با موفقیت به‌روزرسانی شد");
      setIsEditing(false);
      refetchUser();
    } catch (error) {
      toast.error("خطا در به‌روزرسانی پروفایل");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    reset();
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

              {/* Telegram */}
              <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
                <Send className="w-5 h-5 text-muted" />
                <div>
                  <p className="text-sm text-muted">تلگرام</p>
                  <p className="font-medium">
                    {user?.telegram_id
                      ? toPersianNumber(user.telegram_id)
                      : "متصل نشده"}
                  </p>
                </div>
                {user?.telegram_id ? (
                  <Badge variant="success" size="sm" className="mr-auto">
                    <CheckCircle className="w-3 h-3 ml-1" />
                    متصل
                  </Badge>
                ) : (
                  <Link href="/verify" className="mr-auto">
                    <Button variant="outline" size="sm">
                      اتصال
                    </Button>
                  </Link>
                )}
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
              <span className="text-muted">اتصال وب و تلگرام</span>
              {user?.web_linked ? (
                <Badge variant="success">
                  <CheckCircle className="w-3 h-3 ml-1" />
                  همگام شده
                </Badge>
              ) : (
                <Badge variant="outline">
                  <XCircle className="w-3 h-3 ml-1" />
                  جداگانه
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
            با حذف حساب کاربری، تمام اطلاعات و سفارشات شما به طور دائمی حذف خواهد شد.
          </p>
          <Button variant="outline" className="text-danger border-danger hover:bg-danger-light">
            حذف حساب کاربری
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

