"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Palette,
  RefreshCw,
  Plus,
  Package,
  Phone,
  MapPin,
  X,
  Search,
  Briefcase,
  CheckCircle,
  Clock,
  UserX,
  UserCheck,
} from "lucide-react";
import { toPersianNumber } from "@/lib/utils";
import toast from "react-hot-toast";

interface DesignerItem {
  id: string;
  first_name: string;
  last_name?: string;
  phone_number?: string;
  city?: string;
  bio?: string;
  is_active: boolean;
  created_at: string;
  total_orders: number;
  in_progress_orders: number;
  completed_orders: number;
}

export default function AdminDesignersPage() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();

  const [showRegister, setShowRegister] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Form state
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    phone_number: "",
    password: "",
    city: "",
    bio: "",
  });

  // Fetch designers
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["adminDesigners", searchQuery],
    queryFn: async () => {
      const response = await adminApi.getAdminDesigners({
        page: 1,
        page_size: 100,
        ...(searchQuery ? { search: searchQuery } : {}),
      });
      return response.data;
    },
    enabled: isAdmin,
  });

  // Create designer mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      return adminApi.createDesigner({
        first_name: form.first_name,
        last_name: form.last_name || undefined,
        phone_number: form.phone_number,
        password: form.password,
        city: form.city || undefined,
        bio: form.bio || undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminDesigners"] });
      toast.success("طراح جدید با موفقیت ثبت شد");
      setShowRegister(false);
      setForm({
        first_name: "",
        last_name: "",
        phone_number: "",
        password: "",
        city: "",
        bio: "",
      });
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  // Toggle active mutation
  const toggleActiveMutation = useMutation({
    mutationFn: async (designerId: string) => {
      return adminApi.toggleDesignerActive(designerId);
    },
    onSuccess: (_, designerId) => {
      queryClient.invalidateQueries({ queryKey: ["adminDesigners"] });
      toast.success("وضعیت طراح تغییر کرد");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const designers: DesignerItem[] = data?.items ?? [];

  // Stats
  const totalDesigners = data?.total ?? 0;
  const activeDesigners = designers.filter((d) => d.is_active).length;
  const totalInProgress = designers.reduce((sum, d) => sum + d.in_progress_orders, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-foreground">مدیریت طراح‌ها</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRegister(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            افزودن طراح
          </button>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            بروزرسانی
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          type="text"
          placeholder="جستجو بر اساس نام یا شماره تلفن..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pr-10 pl-4 py-2.5 border border-border rounded-xl bg-surface text-foreground placeholder:text-muted focus:ring-2 focus:ring-primary/30 focus:outline-none"
        />
      </div>

      {/* Overview Stats */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-3">نمای کلی</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold">{toPersianNumber(totalDesigners)}</p>
            <p className="text-sm text-muted">تعداد طراح‌ها</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{toPersianNumber(activeDesigners)}</p>
            <p className="text-sm text-muted">طراح‌های فعال</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">{toPersianNumber(totalInProgress)}</p>
            <p className="text-sm text-muted">سفارش در حال طراحی</p>
          </div>
        </div>
      </div>

      {/* Designers List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : designers.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <Palette className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg">هیچ طراحی یافت نشد</p>
          <p className="text-sm mt-1">از دکمه «افزودن طراح» استفاده کنید</p>
        </div>
      ) : (
        <div className="space-y-3">
          {designers.map((designer) => (
            <div
              key={designer.id}
              className="bg-surface border border-border rounded-xl p-5 hover:bg-accent/30 transition-colors"
            >
              <div className="flex flex-col gap-3">
                {/* Row 1: Name + badges + toggle */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Palette className="w-5 h-5 text-primary flex-shrink-0" />
                    <span className="font-semibold text-lg text-foreground">
                      {designer.first_name} {designer.last_name || ""}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs ${
                        designer.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                      }`}
                    >
                      {designer.is_active ? "فعال" : "غیرفعال"}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleActiveMutation.mutate(designer.id);
                    }}
                    disabled={toggleActiveMutation.isPending}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      designer.is_active
                        ? "bg-red-50 text-red-600 hover:bg-red-100 border border-red-200"
                        : "bg-green-50 text-green-600 hover:bg-green-100 border border-green-200"
                    }`}
                  >
                    {designer.is_active ? (
                      <>
                        <UserX className="w-3.5 h-3.5" />
                        غیرفعال کردن
                      </>
                    ) : (
                      <>
                        <UserCheck className="w-3.5 h-3.5" />
                        فعال کردن
                      </>
                    )}
                  </button>
                </div>

                {/* Row 2: Contact info */}
                <div className="flex items-center gap-4 text-sm text-muted flex-wrap">
                  <span className="flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5" />
                    {designer.phone_number || "بدون شماره"}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" />
                    {designer.city || "بدون شهر"}
                  </span>
                </div>

                {/* Row 3: Order stats */}
                <div className="flex items-center gap-4 text-sm flex-wrap">
                  <span className="flex items-center gap-1.5 text-foreground">
                    <Briefcase className="w-3.5 h-3.5 text-primary" />
                    {toPersianNumber(designer.total_orders)} سفارش کل
                  </span>
                  <span className="flex items-center gap-1.5 text-yellow-600">
                    <Clock className="w-3.5 h-3.5" />
                    {toPersianNumber(designer.in_progress_orders)} در حال انجام
                  </span>
                  <span className="flex items-center gap-1.5 text-green-600">
                    <CheckCircle className="w-3.5 h-3.5" />
                    {toPersianNumber(designer.completed_orders)} تکمیل شده
                  </span>
                </div>

                {/* Row 4: Bio (if present) */}
                {designer.bio && (
                  <p className="text-sm text-muted border-t border-border pt-2 mt-1">
                    {designer.bio}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Register Modal */}
      {showRegister && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-foreground">افزودن طراح جدید</h2>
              <button onClick={() => setShowRegister(false)}>
                <X className="w-5 h-5 text-muted hover:text-foreground" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Name row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">نام *</label>
                  <input
                    type="text"
                    value={form.first_name}
                    onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="نام"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">نام خانوادگی</label>
                  <input
                    type="text"
                    value={form.last_name}
                    onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="نام خانوادگی"
                  />
                </div>
              </div>

              {/* Phone + Password */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">شماره تلفن *</label>
                  <input
                    type="text"
                    value={form.phone_number}
                    onChange={(e) => setForm((f) => ({ ...f, phone_number: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="09xxxxxxxxx"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">رمز عبور *</label>
                  <input
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="حداقل ۶ کاراکتر"
                    dir="ltr"
                  />
                </div>
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium mb-1 text-foreground">شهر</label>
                <input
                  type="text"
                  value={form.city}
                  onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  placeholder="مثلاً تهران"
                />
              </div>

              {/* Bio */}
              <div>
                <label className="block text-sm font-medium mb-1 text-foreground">بیوگرافی</label>
                <textarea
                  value={form.bio}
                  onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground resize-none"
                  placeholder="تخصص و تجربه طراح..."
                />
              </div>

              {/* Error */}
              {createMutation.error && (
                <p className="text-sm text-red-600">{getErrorMessage(createMutation.error)}</p>
              )}

              {/* Submit */}
              <button
                onClick={() => createMutation.mutate()}
                disabled={createMutation.isPending || !form.first_name || !form.phone_number || !form.password}
                className="w-full py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? "در حال ثبت..." : "ثبت طراح"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
