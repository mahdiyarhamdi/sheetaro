"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  PageLoading,
  Input,
} from "@/components/ui";
import {
  Users,
  Search,
  ArrowRight,
  Shield,
  User,
  Phone,
  Calendar,
  MoreVertical,
  UserCheck,
  UserX,
  Palette,
  CheckCircle,
  Printer,
  ChevronDown,
  Filter,
} from "lucide-react";
import toast from "react-hot-toast";
import { toPersianNumber, formatDate } from "@/lib/utils";

const ROLES = [
  { value: "CUSTOMER", label: "مشتری", icon: User, color: "bg-accent text-muted" },
  { value: "ADMIN", label: "مدیر", icon: Shield, color: "bg-danger-light text-danger" },
  { value: "DESIGNER", label: "طراح", icon: Palette, color: "bg-primary-50 text-primary" },
  { value: "VALIDATOR", label: "اعتبارسنج", icon: CheckCircle, color: "bg-warning-light text-warning" },
  { value: "PRINT_SHOP", label: "چاپخانه", icon: Printer, color: "bg-success-light text-success" },
];

export default function UsersManagementPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [showRoleMenu, setShowRoleMenu] = useState<string | null>(null);

  // Wait for initial auth check
  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Redirect non-admin users
  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  // Fetch users
  const { data: usersData, isLoading: isLoadingUsers } = useQuery({
    queryKey: ["adminUsers", searchQuery, roleFilter, page],
    queryFn: async () => {
      const response = await adminApi.getUsers({ 
        search: searchQuery || undefined,
        role: roleFilter || undefined,
        page,
        page_size: 20,
      });
      return response.data;
    },
    enabled: isAdmin,
  });

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) => 
      adminApi.updateUserRole(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      toast.success("نقش کاربر به‌روزرسانی شد");
      setShowRoleMenu(null);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Ban user mutation
  const banUserMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      adminApi.banUser(userId, isActive),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      toast.success(variables.isActive ? "کاربر فعال شد" : "کاربر مسدود شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const users = usersData?.items ?? [];
  const totalUsers = usersData?.total ?? 0;
  const totalPages = Math.ceil(totalUsers / 20);

  const getRoleInfo = (role: string) => {
    return ROLES.find(r => r.value === role) ?? ROLES[0];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/admin"
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-foreground">مدیریت کاربران</h1>
            <p className="text-muted mt-1">
              {toPersianNumber(totalUsers)} کاربر در سیستم
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
              <Input
                placeholder="جستجو بر اساس نام یا شماره تلفن..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="pr-10"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => {
                  setRoleFilter(null);
                  setPage(1);
                }}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  !roleFilter ? "bg-primary text-white" : "bg-accent hover:bg-accent/80"
                }`}
              >
                همه
              </button>
              {ROLES.map((role) => (
                <button
                  key={role.value}
                  onClick={() => {
                    setRoleFilter(role.value);
                    setPage(1);
                  }}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    roleFilter === role.value ? "bg-primary text-white" : "bg-accent hover:bg-accent/80"
                  }`}
                >
                  <role.icon className="w-4 h-4" />
                  {role.label}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            لیست کاربران
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingUsers ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-accent rounded-lg animate-pulse" />
              ))}
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-muted">
              <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">کاربری یافت نشد</p>
            </div>
          ) : (
            <div className="space-y-3">
              {users.map((u: any) => {
                const roleInfo = getRoleInfo(u.role);
                return (
                  <div
                    key={u.id}
                    className={`flex items-center justify-between p-4 rounded-xl border transition-colors ${
                      u.is_active 
                        ? "border-border hover:bg-accent/50" 
                        : "border-danger/20 bg-danger-light/10"
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${roleInfo.color}`}>
                        <roleInfo.icon className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-foreground">
                            {u.full_name || `${u.first_name} ${u.last_name || ""}`.trim() || "بدون نام"}
                          </p>
                          {!u.is_active && (
                            <span className="px-2 py-0.5 bg-danger-light text-danger text-xs rounded-full">
                              مسدود
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-muted mt-1">
                          {u.phone_number && (
                            <span className="flex items-center gap-1">
                              <Phone className="w-3.5 h-3.5" />
                              {toPersianNumber(u.phone_number)}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {formatDate(u.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {/* Role dropdown */}
                      <div className="relative">
                        <button
                          onClick={() => setShowRoleMenu(showRoleMenu === u.id ? null : u.id)}
                          className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${roleInfo.color}`}
                        >
                          {roleInfo.label}
                          <ChevronDown className="w-3 h-3" />
                        </button>
                        {showRoleMenu === u.id && (
                          <div className="absolute left-0 mt-2 w-40 bg-surface border border-border rounded-xl shadow-lg z-10">
                            {ROLES.map((role) => (
                              <button
                                key={role.value}
                                onClick={() => updateRoleMutation.mutate({ userId: u.id, role: role.value })}
                                className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors first:rounded-t-xl last:rounded-b-xl ${
                                  u.role === role.value ? "bg-accent" : ""
                                }`}
                              >
                                <role.icon className="w-4 h-4" />
                                {role.label}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      {/* Ban/Unban button */}
                      <button
                        onClick={() => banUserMutation.mutate({ userId: u.id, isActive: !u.is_active })}
                        className={`p-2 rounded-lg transition-colors ${
                          u.is_active 
                            ? "hover:bg-danger-light text-muted hover:text-danger" 
                            : "hover:bg-success-light text-muted hover:text-success"
                        }`}
                        title={u.is_active ? "مسدود کردن" : "فعال کردن"}
                      >
                        {u.is_active ? <UserX className="w-5 h-5" /> : <UserCheck className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                قبلی
              </Button>
              <span className="text-sm text-muted">
                صفحه {toPersianNumber(page)} از {toPersianNumber(totalPages)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                بعدی
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
