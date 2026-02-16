"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AuthLayout } from "@/components/layout";
import { Button, Input } from "@/components/ui";
import { useAuth } from "@/hooks/useAuth";
import { Eye, EyeOff, Phone, Lock, User, Send } from "lucide-react";

const registerSchema = z
  .object({
    full_name: z
      .string()
      .min(2, "نام باید حداقل ۲ کاراکتر باشد")
      .max(255, "نام نباید بیشتر از ۲۵۵ کاراکتر باشد"),
    phone: z
      .string()
      .min(1, "شماره موبایل الزامی است")
      .regex(/^09\d{9}$/, "شماره موبایل نامعتبر است"),
    password: z
      .string()
      .min(6, "رمز عبور باید حداقل ۶ کاراکتر باشد")
      .max(128, "رمز عبور نباید بیشتر از ۱۲۸ کاراکتر باشد"),
    confirmPassword: z.string().min(1, "تکرار رمز عبور الزامی است"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "رمز عبور و تکرار آن مطابقت ندارند",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { register: registerUser, isRegistering } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterFormData) => {
    registerUser({
      full_name: data.full_name,
      phone: data.phone,
      password: data.password,
    });
  };

  return (
    <AuthLayout
      title="ایجاد حساب کاربری"
      description="برای استفاده از خدمات شیتارو ثبت‌نام کنید"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="نام و نام خانوادگی"
          type="text"
          placeholder="مثال: علی محمدی"
          leftIcon={<User className="w-4 h-4" />}
          error={errors.full_name?.message}
          {...register("full_name")}
        />

        <Input
          label="شماره موبایل"
          type="tel"
          placeholder="09123456789"
          leftIcon={<Phone className="w-4 h-4" />}
          error={errors.phone?.message}
          {...register("phone")}
          dir="ltr"
        />

        <div className="relative">
          <Input
            label="رمز عبور"
            type={showPassword ? "text" : "password"}
            placeholder="حداقل ۶ کاراکتر"
            leftIcon={<Lock className="w-4 h-4" />}
            error={errors.password?.message}
            {...register("password")}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute left-10 top-[38px] text-muted hover:text-foreground transition-colors"
          >
            {showPassword ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </button>
        </div>

        <div className="relative">
          <Input
            label="تکرار رمز عبور"
            type={showConfirmPassword ? "text" : "password"}
            placeholder="رمز عبور را تکرار کنید"
            leftIcon={<Lock className="w-4 h-4" />}
            error={errors.confirmPassword?.message}
            {...register("confirmPassword")}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute left-10 top-[38px] text-muted hover:text-foreground transition-colors"
          >
            {showConfirmPassword ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </button>
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full"
          isLoading={isRegistering}
        >
          ثبت‌نام
        </Button>
      </form>

      {/* Terms */}
      <p className="mt-4 text-xs text-center text-muted">
        با ثبت‌نام،{" "}
        <Link href="/terms" className="text-primary hover:underline">
          قوانین و مقررات
        </Link>{" "}
        و{" "}
        <Link href="/privacy" className="text-primary hover:underline">
          حریم خصوصی
        </Link>{" "}
        را می‌پذیرید
      </p>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-surface px-2 text-muted">یا</span>
        </div>
      </div>

      {/* Telegram register */}
      <a
        href="https://t.me/sheetarobot?start=register"
        target="_blank"
        rel="noopener noreferrer"
        className="w-full"
      >
        <Button
          type="button"
          variant="outline"
          className="w-full"
          leftIcon={<Send className="w-4 h-4" />}
        >
          ثبت‌نام با تلگرام
        </Button>
      </a>

      {/* Login link */}
      <p className="mt-6 text-center text-sm text-muted">
        قبلاً ثبت‌نام کرده‌اید؟{" "}
        <Link
          href="/login"
          className="text-primary font-medium hover:text-primary-800 transition-colors"
        >
          وارد شوید
        </Link>
      </p>
    </AuthLayout>
  );
}

