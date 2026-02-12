"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Home,
  Package,
  ShoppingCart,
  User,
  Settings,
  CreditCard,
  FolderOpen,
  Users,
  BarChart3,
  X,
  MessageCircle,
  Type,
  CheckSquare,
  Factory,
  ClipboardList,
  DollarSign,
  Truck,
  Palette,
  PenTool,
  Inbox,
} from "lucide-react";
import { useEffect, useState } from "react";
import { isAdmin, isPrintShop, isDesigner } from "../../lib/auth";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

const customerNavItems: NavItem[] = [
  { href: "/", label: "داشبورد", icon: Home },
  { href: "/orders", label: "سفارشات من", icon: Package },
  { href: "/new-order", label: "سفارش جدید", icon: ShoppingCart },
  { href: "/profile", label: "پروفایل", icon: User },
];

const adminNavItems: NavItem[] = [
  { href: "/admin", label: "داشبورد مدیریت", icon: BarChart3 },
  { href: "/admin/payments", label: "پرداخت‌ها", icon: CreditCard },
  { href: "/admin/validations", label: "اعتبارسنجی‌ها", icon: CheckSquare },
  { href: "/admin/catalog", label: "مدیریت کاتالوگ", icon: FolderOpen },
  { href: "/admin/fonts", label: "مدیریت فونت‌ها", icon: Type },
  { href: "/admin/users", label: "کاربران", icon: Users },
  { href: "/admin/printshops", label: "مدیریت چاپخانه‌ها", icon: Factory },
];

const designerNavItems: NavItem[] = [
  { href: "/designer", label: "داشبورد طراح", icon: Palette },
  { href: "/designer/queue", label: "صف سفارشات جدید", icon: Inbox },
  { href: "/designer/orders", label: "سفارشات من", icon: PenTool },
];

const printShopNavItems: NavItem[] = [
  { href: "/printshop", label: "داشبورد چاپخانه", icon: Factory },
  { href: "/printshop/orders", label: "صف سفارش‌ها", icon: ClipboardList },
  { href: "/printshop/my-orders", label: "سفارش‌های من", icon: Truck },
  { href: "/printshop/settlements", label: "تسویه‌حساب", icon: DollarSign },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [isUserAdmin, setIsUserAdmin] = useState(false);
  const [isUserPrintShop, setIsUserPrintShop] = useState(false);
  const [isUserDesigner, setIsUserDesigner] = useState(false);

  useEffect(() => {
    setIsUserAdmin(isAdmin());
    setIsUserPrintShop(isPrintShop());
    setIsUserDesigner(isDesigner());
  }, []);

  const isActiveLink = (href: string) => {
    if (href === "/") return pathname === "/";
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 right-0 bottom-0 z-50 w-64 bg-surface border-l border-border",
          "transform transition-transform duration-300 ease-in-out",
          "lg:static lg:transform-none",
          isOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"
        )}
      >
        {/* Mobile close button */}
        <div className="flex items-center justify-between p-4 border-b border-border lg:hidden">
          <span className="font-semibold text-foreground">منو</span>
          <button
            onClick={onClose}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
            aria-label="بستن منو"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-65px)] lg:h-screen">
          {/* Customer navigation */}
          <div>
            <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
              منو اصلی
            </h3>
            <ul className="space-y-1">
              {customerNavItems.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onClose}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                      isActiveLink(item.href)
                        ? "bg-primary-50 text-primary"
                        : "text-muted hover:bg-accent hover:text-foreground"
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                    {item.badge && (
                      <span className="mr-auto bg-primary text-white text-xs px-2 py-0.5 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Designer navigation */}
          {isUserDesigner && (
            <div>
              <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
                پنل طراح
              </h3>
              <ul className="space-y-1">
                {designerNavItems.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        isActiveLink(item.href)
                          ? "bg-primary-50 text-primary"
                          : "text-muted hover:bg-accent hover:text-foreground"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Print Shop navigation */}
          {isUserPrintShop && (
            <div>
              <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
                پنل چاپخانه
              </h3>
              <ul className="space-y-1">
                {printShopNavItems.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        isActiveLink(item.href)
                          ? "bg-primary-50 text-primary"
                          : "text-muted hover:bg-accent hover:text-foreground"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Admin navigation */}
          {isUserAdmin && (
            <div>
              <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
                پنل مدیریت
              </h3>
              <ul className="space-y-1">
                {adminNavItems.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        isActiveLink(item.href)
                          ? "bg-primary-50 text-primary"
                          : "text-muted hover:bg-accent hover:text-foreground"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Support link */}
          <div className="pt-4 border-t border-border">
            <Link
              href="/support"
              onClick={onClose}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted hover:bg-accent hover:text-foreground transition-colors"
            >
              <MessageCircle className="w-5 h-5" />
              <span>پشتیبانی</span>
            </Link>
          </div>
        </nav>
      </aside>
    </>
  );
}

