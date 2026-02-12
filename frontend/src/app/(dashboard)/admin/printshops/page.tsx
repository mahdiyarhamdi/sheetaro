"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import {
  Factory,
  RefreshCw,
  Plus,
  Star,
  Package,
  Phone,
  MapPin,
  X,
  Search,
  Shield,
  Tag,
} from "lucide-react";
import { formatPrice, toPersianNumber } from "@/lib/utils";

export default function AdminPrintShopsPage() {
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
    description: "",
    capabilities: [] as string[],
    service_areas: [] as string[],
    max_daily_capacity: "",
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["adminPrintshops", searchQuery],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshops({
        page: 1,
        page_size: 100,
        ...(searchQuery ? { search: searchQuery } : {}),
      });
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: slaReport } = useQuery({
    queryKey: ["adminSlaReport"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopSlaReport();
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: capabilitiesData } = useQuery({
    queryKey: ["printshopCapabilities"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopCapabilities();
      return response.data;
    },
    enabled: isAdmin,
  });

  const capabilities = capabilitiesData?.capabilities ?? [];

  const createMutation = useMutation({
    mutationFn: async () => {
      return adminApi.createPrintshop({
        first_name: form.first_name,
        last_name: form.last_name || undefined,
        phone_number: form.phone_number,
        password: form.password,
        city: form.city || undefined,
        description: form.description || undefined,
        capabilities: form.capabilities,
        service_areas: form.service_areas,
        max_daily_capacity: form.max_daily_capacity ? Number(form.max_daily_capacity) : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshops"] });
      setShowRegister(false);
      setForm({
        first_name: "",
        last_name: "",
        phone_number: "",
        password: "",
        city: "",
        description: "",
        capabilities: [],
        service_areas: [],
        max_daily_capacity: "",
      });
    },
  });

  const printshops = data?.items ?? [];

  const toggleCapability = (cap: string) => {
    setForm((prev) => ({
      ...prev,
      capabilities: prev.capabilities.includes(cap)
        ? prev.capabilities.filter((c) => c !== cap)
        : [...prev.capabilities, cap],
    }));
  };

  const renderStars = (rating: number | null) => {
    if (rating == null) return <span className="text-xs text-muted">بدون امتیاز</span>;
    const rounded = Math.round(rating * 10) / 10;
    return (
      <span className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star
            key={s}
            className={`w-3.5 h-3.5 ${s <= Math.round(rating) ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`}
          />
        ))}
        <span className="text-xs font-semibold mr-1">{toPersianNumber(rounded.toFixed(1))}</span>
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-foreground">مدیریت چاپخانه‌ها</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRegister(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            ثبت چاپخانه جدید
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

      {/* SLA Overview */}
      {slaReport && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-3">نمای کلی</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{toPersianNumber(slaReport.queue_size ?? 0)}</p>
              <p className="text-sm text-muted">صف انتظار</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{toPersianNumber(printshops.length)}</p>
              <p className="text-sm text-muted">تعداد چاپخانه</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {toPersianNumber(slaReport.printshops?.length ?? 0)}
              </p>
              <p className="text-sm text-muted">چاپخانه‌ها با SLA</p>
            </div>
          </div>
        </div>
      )}

      {/* Print Shops List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : printshops.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <Factory className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg">هیچ چاپخانه‌ای یافت نشد</p>
          <p className="text-sm mt-1">از دکمه «ثبت چاپخانه جدید» استفاده کنید</p>
        </div>
      ) : (
        <div className="space-y-3">
          {printshops.map((ps: Record<string, unknown>) => {
            const slaInfo = slaReport?.printshops?.find(
              (p: Record<string, unknown>) => p.printshop_id === ps.id
            );
            const isAdminRole = ps.role === "ADMIN";
            const capList = (ps.capabilities as string[]) || [];
            const avgRating = ps.avg_rating as number | null;
            const reviewCount = (ps.review_count as number) || 0;
            const totalOrders = (ps.total_orders as number) || 0;

            return (
              <Link
                key={ps.id as string}
                href={`/admin/printshops/${ps.id}`}
                className="block bg-surface border border-border rounded-xl p-5 hover:bg-accent transition-colors"
              >
                <div className="flex flex-col gap-3">
                  {/* Row 1: Name + badges */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Factory className="w-5 h-5 text-primary flex-shrink-0" />
                      <span className="font-semibold text-lg">
                        {ps.first_name as string} {(ps.last_name as string) || ""}
                      </span>
                      {isAdminRole && (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-purple-100 text-purple-700">
                          <Shield className="w-3 h-3" />
                          مدیر
                        </span>
                      )}
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          ps.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                        }`}
                      >
                        {ps.is_active ? "فعال" : "غیرفعال"}
                      </span>
                      {Boolean(ps.is_featured) && (
                        <span className="px-2 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700">
                          ویژه
                        </span>
                      )}
                    </div>
                    <div className="text-left">{renderStars(avgRating)}</div>
                  </div>

                  {/* Row 2: Info */}
                  <div className="flex items-center gap-4 text-sm text-muted flex-wrap">
                    <span className="flex items-center gap-1">
                      <Phone className="w-3.5 h-3.5" />
                      {(ps.phone_number as string) || "بدون شماره"}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5" />
                      {(ps.city as string) || "بدون شهر"}
                    </span>
                    <span className="flex items-center gap-1">
                      <Package className="w-3.5 h-3.5" />
                      {toPersianNumber(totalOrders)} سفارش
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="w-3.5 h-3.5" />
                      {toPersianNumber(reviewCount)} نظر
                    </span>
                  </div>

                  {/* Row 3: Capabilities */}
                  {capList.length > 0 && (
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {capList.slice(0, 5).map((cap: string) => (
                        <span
                          key={cap}
                          className="flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-blue-50 text-blue-700 border border-blue-200"
                        >
                          <Tag className="w-3 h-3" />
                          {cap}
                        </span>
                      ))}
                      {capList.length > 5 && (
                        <span className="text-xs text-muted">
                          +{toPersianNumber(capList.length - 5)} مورد دیگر
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Register Modal */}
      {showRegister && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">ثبت چاپخانه جدید</h2>
              <button onClick={() => setShowRegister(false)}>
                <X className="w-5 h-5 text-muted hover:text-foreground" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Name row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">نام *</label>
                  <input
                    type="text"
                    value={form.first_name}
                    onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="نام"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">نام خانوادگی</label>
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
                  <label className="block text-sm font-medium mb-1">شماره تلفن *</label>
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
                  <label className="block text-sm font-medium mb-1">رمز عبور *</label>
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

              {/* City + Capacity */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">شهر</label>
                  <input
                    type="text"
                    value={form.city}
                    onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="مثلاً تهران"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">ظرفیت روزانه</label>
                  <input
                    type="number"
                    value={form.max_daily_capacity}
                    onChange={(e) => setForm((f) => ({ ...f, max_daily_capacity: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                    placeholder="تعداد سفارش"
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium mb-1">توضیحات</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground resize-none"
                  placeholder="درباره چاپخانه..."
                />
              </div>

              {/* Capabilities */}
              <div>
                <label className="block text-sm font-medium mb-2">توانمندی‌ها</label>
                <div className="flex flex-wrap gap-2">
                  {capabilities.map((cap: string) => (
                    <button
                      key={cap}
                      type="button"
                      onClick={() => toggleCapability(cap)}
                      className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                        form.capabilities.includes(cap)
                          ? "bg-primary text-white border-primary"
                          : "bg-background text-foreground border-border hover:border-primary/50"
                      }`}
                    >
                      {cap}
                    </button>
                  ))}
                </div>
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
                {createMutation.isPending ? "در حال ثبت..." : "ثبت چاپخانه"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
