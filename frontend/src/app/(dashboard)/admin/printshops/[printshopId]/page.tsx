"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { formatPrice, toPersianNumber } from "@/lib/utils";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
  ArrowRight,
  Package,
  Clock,
  CheckCircle,
  Truck,
  Star,
  MessageSquare,
  ThumbsUp,
  Trash2,
  Tag,
  MapPin,
  Phone,
  CalendarDays,
  Shield,
  Edit2,
  Power,
  Save,
  X,
  Info,
  User,
  Award,
} from "lucide-react";
import { useState } from "react";

const statusLabels: Record<string, string> = {
  PRINTING: "در حال چاپ",
  PRINTED: "چاپ شده",
  SHIPPED: "ارسال شده",
  DELIVERED: "تحویل شده",
  CANCELLED: "لغو شده",
};

const statusColors: Record<string, string> = {
  PRINTING: "bg-blue-100 text-blue-700",
  PRINTED: "bg-purple-100 text-purple-700",
  SHIPPED: "bg-orange-100 text-orange-700",
  DELIVERED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
};

export default function AdminPrintShopDetailPage() {
  const { printshopId } = useParams<{ printshopId: string }>();
  const router = useRouter();
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("info");
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    description: "",
    capabilities: [] as string[],
    max_daily_capacity: "",
    service_areas: [] as string[],
    is_featured: false,
  });

  // Profile query
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["adminPrintshopProfile", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshopProfile(printshopId);
      return response.data;
    },
    enabled: isAdmin && !!printshopId,
  });

  // Capabilities list
  const { data: capabilitiesData } = useQuery({
    queryKey: ["printshopCapabilities"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopCapabilities();
      return response.data;
    },
    enabled: isAdmin,
  });
  const allCapabilities = capabilitiesData?.capabilities ?? [];

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["adminPrintshopStats", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshopStats(printshopId);
      return response.data;
    },
    enabled: isAdmin && !!printshopId,
  });

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ["adminPrintshopOrders", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshopOrders(printshopId, {
        page: 1,
        page_size: 50,
      });
      return response.data;
    },
    enabled: isAdmin && !!printshopId && activeTab === "orders",
  });

  const { data: settlementsData, isLoading: settlementsLoading } = useQuery({
    queryKey: ["adminPrintshopSettlements", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminSettlements({
        page: 1,
        page_size: 50,
        printshop_id: printshopId,
      });
      return response.data;
    },
    enabled: isAdmin && !!printshopId && activeTab === "settlements",
  });

  const { data: reviewsData, isLoading: reviewsLoading } = useQuery({
    queryKey: ["adminPrintshopReviews", printshopId],
    queryFn: async () => {
      const response = await adminApi.getReviews({
        printshop_id: printshopId,
        page: 1,
        page_size: 50,
      });
      return response.data;
    },
    enabled: isAdmin && !!printshopId && activeTab === "reviews",
  });

  // Mutations
  const paySettlement = useMutation({
    mutationFn: (settlementId: string) => adminApi.markSettlementPaid(settlementId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopSettlements", printshopId] });
    },
  });

  const approveReview = useMutation({
    mutationFn: (reviewId: string) => adminApi.approveReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopReviews", printshopId] });
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopProfile", printshopId] });
    },
  });

  const rejectReview = useMutation({
    mutationFn: (reviewId: string) => adminApi.rejectReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopReviews", printshopId] });
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopProfile", printshopId] });
    },
  });

  const updateProfile = useMutation({
    mutationFn: () =>
      adminApi.updatePrintshopProfile(printshopId, {
        description: editForm.description || undefined,
        capabilities: editForm.capabilities,
        max_daily_capacity: editForm.max_daily_capacity ? Number(editForm.max_daily_capacity) : undefined,
        service_areas: editForm.service_areas,
        is_featured: editForm.is_featured,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopProfile", printshopId] });
      queryClient.invalidateQueries({ queryKey: ["adminPrintshops"] });
      setEditing(false);
    },
  });

  const toggleActive = useMutation({
    mutationFn: () => adminApi.togglePrintshopActive(printshopId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopProfile", printshopId] });
      queryClient.invalidateQueries({ queryKey: ["adminPrintshops"] });
    },
  });

  const orders = ordersData?.items ?? [];
  const settlements = settlementsData?.items ?? [];
  const reviews = reviewsData?.items ?? [];

  const startEditing = () => {
    if (profile) {
      setEditForm({
        description: profile.description || "",
        capabilities: profile.capabilities || [],
        max_daily_capacity: profile.max_daily_capacity ? String(profile.max_daily_capacity) : "",
        service_areas: profile.service_areas || [],
        is_featured: profile.is_featured || false,
      });
      setEditing(true);
    }
  };

  const toggleEditCapability = (cap: string) => {
    setEditForm((prev) => ({
      ...prev,
      capabilities: prev.capabilities.includes(cap)
        ? prev.capabilities.filter((c) => c !== cap)
        : [...prev.capabilities, cap],
    }));
  };

  const renderStars = (rating: number | null, size = "w-4 h-4") => {
    if (rating == null) return <span className="text-sm text-muted">بدون امتیاز</span>;
    return (
      <span className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star
            key={s}
            className={`${size} ${s <= Math.round(rating) ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`}
          />
        ))}
        <span className="text-sm font-semibold mr-1">
          {toPersianNumber((Math.round(rating * 10) / 10).toFixed(1))}
        </span>
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/admin/printshops")}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
        >
          <ArrowRight className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-foreground">
            {profile ? `${profile.first_name} ${profile.last_name || ""}` : "جزئیات چاپخانه"}
          </h1>
          {profile && (
            <div className="flex items-center gap-2 mt-1">
              {profile.role === "ADMIN" && (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-purple-100 text-purple-700">
                  <Shield className="w-3 h-3" />
                  مدیر
                </span>
              )}
              <span
                className={`px-2 py-0.5 rounded-full text-xs ${
                  profile.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                }`}
              >
                {profile.is_active ? "فعال" : "غیرفعال"}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      {statsLoading ? (
        <div className="flex items-center justify-center min-h-[100px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Package className="w-6 h-6 mx-auto text-blue-500 mb-2" />
            <p className="text-xl font-bold">{toPersianNumber(stats.total_orders ?? 0)}</p>
            <p className="text-sm text-muted">کل سفارش‌ها</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <CheckCircle className="w-6 h-6 mx-auto text-green-500 mb-2" />
            <p className="text-xl font-bold">{toPersianNumber(stats.printed ?? 0)}</p>
            <p className="text-sm text-muted">چاپ شده</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Truck className="w-6 h-6 mx-auto text-orange-500 mb-2" />
            <p className="text-xl font-bold">{toPersianNumber(stats.shipped ?? 0)}</p>
            <p className="text-sm text-muted">ارسال شده</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Clock className="w-6 h-6 mx-auto text-purple-500 mb-2" />
            <p className="text-xl font-bold">
              {stats.avg_print_time_hours != null
                ? `${Number(stats.avg_print_time_hours).toFixed(1)}h`
                : "-"}
            </p>
            <p className="text-sm text-muted">میانگین زمان چاپ</p>
          </div>
        </div>
      ) : null}

      {/* Tabs */}
      <div className="flex border-b border-border overflow-x-auto">
        {[
          { key: "info", label: "اطلاعات", icon: Info },
          { key: "orders", label: "سفارش‌ها", icon: Package },
          { key: "settlements", label: "تسویه‌حساب", icon: Award },
          { key: "reviews", label: "نظرات", icon: MessageSquare, count: reviewsData?.total },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-muted hover:text-foreground"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
            {tab.count ? (
              <span className="px-1.5 py-0.5 bg-primary/10 text-primary text-xs rounded-full">
                {toPersianNumber(tab.count)}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {/* =================== INFO TAB =================== */}
      {activeTab === "info" && (
        <div className="space-y-6">
          {profileLoading ? (
            <div className="flex items-center justify-center min-h-[200px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : profile ? (
            <>
              {/* Action buttons */}
              <div className="flex items-center gap-2 flex-wrap">
                {!editing ? (
                  <button
                    onClick={startEditing}
                    className="flex items-center gap-1.5 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm"
                  >
                    <Edit2 className="w-4 h-4" />
                    ویرایش
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => updateProfile.mutate()}
                      disabled={updateProfile.isPending}
                      className="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm disabled:opacity-50"
                    >
                      <Save className="w-4 h-4" />
                      {updateProfile.isPending ? "ذخیره..." : "ذخیره"}
                    </button>
                    <button
                      onClick={() => setEditing(false)}
                      className="flex items-center gap-1.5 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
                    >
                      <X className="w-4 h-4" />
                      انصراف
                    </button>
                  </>
                )}
                {profile.role !== "ADMIN" && (
                  <button
                    onClick={() => {
                      if (confirm(profile.is_active ? "غیرفعال کردن این چاپخانه؟" : "فعال کردن این چاپخانه؟"))
                        toggleActive.mutate();
                    }}
                    disabled={toggleActive.isPending}
                    className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50 ${
                      profile.is_active
                        ? "bg-red-100 text-red-700 hover:bg-red-200"
                        : "bg-green-100 text-green-700 hover:bg-green-200"
                    }`}
                  >
                    <Power className="w-4 h-4" />
                    {profile.is_active ? "غیرفعال‌سازی" : "فعال‌سازی"}
                  </button>
                )}
              </div>

              {updateProfile.error && (
                <p className="text-sm text-red-600">{getErrorMessage(updateProfile.error)}</p>
              )}

              {/* Profile grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left column - Basic info */}
                <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
                  <h3 className="font-semibold text-lg flex items-center gap-2">
                    <User className="w-5 h-5 text-primary" />
                    اطلاعات پایه
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted">نام</span>
                      <span className="font-medium">{profile.full_name || `${profile.first_name} ${profile.last_name || ""}`}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted flex items-center gap-1"><Phone className="w-3.5 h-3.5" /> تلفن</span>
                      <span className="font-medium" dir="ltr">{profile.phone_number || "-"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> شهر</span>
                      <span className="font-medium">{profile.city || "-"}</span>
                    </div>
                    {profile.address && (
                      <div className="flex justify-between">
                        <span className="text-muted">آدرس</span>
                        <span className="font-medium text-left max-w-[60%]">{profile.address}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-muted flex items-center gap-1"><CalendarDays className="w-3.5 h-3.5" /> تاریخ عضویت</span>
                      <span className="font-medium">
                        {profile.user_created_at
                          ? new Date(profile.user_created_at).toLocaleDateString("fa-IR")
                          : "-"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted">نقش</span>
                      <span className="font-medium">{profile.role === "ADMIN" ? "مدیر" : "چاپخانه"}</span>
                    </div>
                  </div>
                </div>

                {/* Right column - Rating & Stats */}
                <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
                  <h3 className="font-semibold text-lg flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-500" />
                    امتیاز و عملکرد
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">میانگین امتیاز</span>
                      {renderStars(profile.avg_rating, "w-5 h-5")}
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted">تعداد نظرات</span>
                      <span className="font-medium">{toPersianNumber(profile.review_count ?? 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted">کل سفارش‌ها</span>
                      <span className="font-medium">{toPersianNumber(profile.total_orders ?? 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted">ظرفیت روزانه</span>
                      <span className="font-medium">
                        {editing
                          ? "-"
                          : profile.max_daily_capacity
                          ? `${toPersianNumber(profile.max_daily_capacity)} سفارش`
                          : "تنظیم نشده"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted">ویژه</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${profile.is_featured ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-600"}`}>
                        {profile.is_featured ? "بله" : "خیر"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="bg-surface border border-border rounded-xl p-6 space-y-3">
                <h3 className="font-semibold text-lg">درباره چاپخانه</h3>
                {editing ? (
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm((f) => ({ ...f, description: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground resize-none"
                    placeholder="توضیحات درباره چاپخانه..."
                  />
                ) : (
                  <p className="text-foreground">{profile.description || "توضیحاتی ثبت نشده"}</p>
                )}
              </div>

              {/* Capabilities */}
              <div className="bg-surface border border-border rounded-xl p-6 space-y-3">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <Tag className="w-5 h-5 text-blue-500" />
                  توانمندی‌ها
                </h3>
                {editing ? (
                  <div className="flex flex-wrap gap-2">
                    {allCapabilities.map((cap: string) => (
                      <button
                        key={cap}
                        type="button"
                        onClick={() => toggleEditCapability(cap)}
                        className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                          editForm.capabilities.includes(cap)
                            ? "bg-primary text-white border-primary"
                            : "bg-background text-foreground border-border hover:border-primary/50"
                        }`}
                      >
                        {cap}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {(profile.capabilities || []).length === 0 ? (
                      <p className="text-muted text-sm">توانمندی ثبت نشده</p>
                    ) : (
                      (profile.capabilities || []).map((cap: string) => (
                        <span
                          key={cap}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs bg-blue-50 text-blue-700 border border-blue-200"
                        >
                          <Tag className="w-3 h-3" />
                          {cap}
                        </span>
                      ))
                    )}
                  </div>
                )}
              </div>

              {/* Service areas */}
              <div className="bg-surface border border-border rounded-xl p-6 space-y-3">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-green-500" />
                  مناطق سرویس‌دهی
                </h3>
                {editing ? (
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      {editForm.service_areas.map((area, i) => (
                        <span
                          key={i}
                          className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs bg-green-50 text-green-700 border border-green-200"
                        >
                          {area}
                          <button
                            onClick={() =>
                              setEditForm((f) => ({
                                ...f,
                                service_areas: f.service_areas.filter((_, idx) => idx !== i),
                              }))
                            }
                            className="text-green-500 hover:text-red-500"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                    <input
                      type="text"
                      placeholder="نام شهر + Enter"
                      className="px-3 py-2 border border-border rounded-lg bg-background text-foreground text-sm w-48"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          const v = (e.target as HTMLInputElement).value.trim();
                          if (v && !editForm.service_areas.includes(v)) {
                            setEditForm((f) => ({
                              ...f,
                              service_areas: [...f.service_areas, v],
                            }));
                            (e.target as HTMLInputElement).value = "";
                          }
                          e.preventDefault();
                        }
                      }}
                    />
                    {/* Capacity in edit mode */}
                    <div className="mt-3">
                      <label className="block text-sm font-medium mb-1">ظرفیت روزانه</label>
                      <input
                        type="number"
                        value={editForm.max_daily_capacity}
                        onChange={(e) => setEditForm((f) => ({ ...f, max_daily_capacity: e.target.value }))}
                        className="px-3 py-2 border border-border rounded-lg bg-background text-foreground text-sm w-48"
                        placeholder="تعداد سفارش"
                        dir="ltr"
                      />
                    </div>
                    {/* Featured toggle */}
                    <div className="mt-3 flex items-center gap-2">
                      <label className="text-sm font-medium">چاپخانه ویژه:</label>
                      <button
                        onClick={() => setEditForm((f) => ({ ...f, is_featured: !f.is_featured }))}
                        className={`px-3 py-1 rounded-lg text-xs border transition-colors ${
                          editForm.is_featured
                            ? "bg-yellow-100 text-yellow-700 border-yellow-300"
                            : "bg-gray-100 text-gray-600 border-gray-300"
                        }`}
                      >
                        {editForm.is_featured ? "بله" : "خیر"}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {(profile.service_areas || []).length === 0 ? (
                      <p className="text-muted text-sm">منطقه سرویس‌دهی ثبت نشده</p>
                    ) : (
                      (profile.service_areas || []).map((area: string) => (
                        <span
                          key={area}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs bg-green-50 text-green-700 border border-green-200"
                        >
                          <MapPin className="w-3 h-3" />
                          {area}
                        </span>
                      ))
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <p className="text-center py-8 text-muted">پروفایل یافت نشد</p>
          )}
        </div>
      )}

      {/* =================== ORDERS TAB =================== */}
      {activeTab === "orders" && (
        <div className="space-y-3">
          {ordersLoading ? (
            <div className="flex items-center justify-center min-h-[100px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : orders.length === 0 ? (
            <p className="text-center py-8 text-muted">سفارشی یافت نشد</p>
          ) : (
            orders.map((o: Record<string, unknown>) => (
              <div
                key={o.id as string}
                className="bg-surface border border-border rounded-xl p-4 flex items-center justify-between"
              >
                <div className="space-y-1">
                  <p className="font-medium">سفارش #{(o.id as string).slice(0, 8)}</p>
                  <p className="text-sm text-muted">
                    {o.quantity as number} عدد · {(o.customer_city as string) || "بدون شهر"}
                  </p>
                </div>
                <div className="text-left">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs ${
                      statusColors[o.status as string] ?? "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {statusLabels[o.status as string] ?? (o.status as string)}
                  </span>
                  <p className="text-sm text-muted mt-1">{formatPrice(o.total_price as number)}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* =================== SETTLEMENTS TAB =================== */}
      {activeTab === "settlements" && (
        <div className="space-y-3">
          {settlementsLoading ? (
            <div className="flex items-center justify-center min-h-[100px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : settlements.length === 0 ? (
            <p className="text-center py-8 text-muted">تسویه‌حسابی یافت نشد</p>
          ) : (
            settlements.map((s: Record<string, unknown>) => (
              <div
                key={s.id as string}
                className="bg-surface border border-border rounded-xl p-4 flex items-center justify-between"
              >
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {s.period_start as string} تا {s.period_end as string}
                  </p>
                  <p className="text-sm text-muted">
                    {toPersianNumber(s.total_orders as number)} سفارش · {formatPrice(s.net_amount as number)}
                  </p>
                </div>
                <div className="text-left">
                  {s.status === "PAID" ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      پرداخت شده
                    </span>
                  ) : (
                    <button
                      onClick={() => paySettlement.mutate(s.id as string)}
                      disabled={paySettlement.isPending}
                      className="px-3 py-1 bg-primary text-white rounded-lg text-xs hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                      {paySettlement.isPending ? "..." : "تسویه"}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* =================== REVIEWS TAB =================== */}
      {activeTab === "reviews" && (
        <div className="space-y-3">
          {reviewsLoading ? (
            <div className="flex items-center justify-center min-h-[100px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-8 text-muted">
              <MessageSquare className="w-10 h-10 mx-auto mb-3 opacity-50" />
              <p>هنوز نظری ثبت نشده</p>
            </div>
          ) : (
            reviews.map((r: Record<string, unknown>) => (
              <div
                key={r.id as string}
                className={`bg-surface border rounded-xl p-4 ${
                  r.is_approved ? "border-green-200" : "border-border"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-medium text-foreground">
                        {(r.user_name as string) || "کاربر"}
                      </span>
                      {(r.user_phone as string) && (
                        <span className="text-muted" dir="ltr">
                          {r.user_phone as string}
                        </span>
                      )}
                      <span className="text-muted">·</span>
                      <span className="text-muted">سفارش #{(r.order_id as string).slice(0, 8)}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-4 h-4 ${
                            star <= (r.rating as number)
                              ? "text-yellow-400 fill-yellow-400"
                              : "text-gray-300"
                          }`}
                        />
                      ))}
                      <span className="text-xs text-muted mr-1">({r.rating as number}/5)</span>
                    </div>
                    {(r.comment as string) && (
                      <p className="text-sm text-foreground bg-accent/50 p-2 rounded-lg">
                        {r.comment as string}
                      </p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-muted">
                      <span>{new Date(r.created_at as string).toLocaleDateString("fa-IR")}</span>
                      {r.is_approved ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                          <CheckCircle className="w-3 h-3" />
                          تایید شده
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full">
                          <Clock className="w-3 h-3" />
                          در انتظار تایید
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    {!r.is_approved && (
                      <button
                        onClick={() => approveReview.mutate(r.id as string)}
                        disabled={approveReview.isPending}
                        className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs hover:bg-green-700 transition-colors disabled:opacity-50"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        تایید
                      </button>
                    )}
                    <button
                      onClick={() => {
                        if (confirm("آیا از حذف این نظر مطمئنید?")) {
                          rejectReview.mutate(r.id as string);
                        }
                      }}
                      disabled={rejectReview.isPending}
                      className="flex items-center gap-1 px-3 py-1.5 bg-red-100 text-red-700 rounded-lg text-xs hover:bg-red-200 transition-colors disabled:opacity-50"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      حذف
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
