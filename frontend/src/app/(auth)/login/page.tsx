"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AuthLayout } from "@/components/layout";
import { Button, Input } from "@/components/ui";
import { useAuth } from "@/hooks/useAuth";
import { Eye, EyeOff, Phone, Lock, Send } from "lucide-react";

const loginSchema = z.object({
  phone: z
    .string()
    .min(1, "شماره موبایل الزامی است")
    .regex(/^09\d{9}$/, "شماره موبایل نامعتبر است"),
  password: z.string().min(1, "رمز عبور الزامی است"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoggingIn } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormData) => {
    login(data);
  };

  return (
    <AuthLayout
      title="ورود به حساب"
      description="خوش آمدید! برای ادامه وارد شوید"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
            placeholder="رمز عبور خود را وارد کنید"
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

        <div className="flex items-center justify-between text-sm">
          <Link
            href="/forgot-password"
            className="text-primary hover:text-primary-800 transition-colors"
          >
            فراموشی رمز عبور
          </Link>
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full"
          isLoading={isLoggingIn}
        >
          ورود
        </Button>
      </form>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-surface px-2 text-muted">یا</span>
        </div>
      </div>

      {/* Telegram login */}
      <a
        href="https://t.me/sheetaro_bot?start=login"
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
          ورود با تلگرام
        </Button>
      </a>

      {/* Register link */}
      <p className="mt-6 text-center text-sm text-muted">
        حساب کاربری ندارید؟{" "}
        <Link
          href="/register"
          className="text-primary font-medium hover:text-primary-800 transition-colors"
        >
          ثبت‌نام کنید
        </Link>
      </p>
    </AuthLayout>
  );
}

