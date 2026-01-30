"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Menu,
  X,
  User,
  LogOut,
  Settings,
  ShoppingCart,
  Package,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";

interface HeaderProps {
  onMenuToggle?: () => void;
  isSidebarOpen?: boolean;
}

// Direct localStorage access (only on client)
function getAuthFromStorage() {
  if (typeof window === "undefined") return { isLoggedIn: false, user: null };
  
  const token = localStorage.getItem("access_token");
  const userStr = localStorage.getItem("user");
  
  if (!token) return { isLoggedIn: false, user: null };
  
  try {
    const user = userStr ? JSON.parse(userStr) : null;
    return { isLoggedIn: true, user };
  } catch {
    return { isLoggedIn: true, user: null };
  }
}

export function Header({ onMenuToggle, isSidebarOpen }: HeaderProps) {
  const pathname = usePathname();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  
  // Auth state - start with null to indicate "checking"
  const [authState, setAuthState] = useState<{
    checked: boolean;
    isLoggedIn: boolean;
    user: any;
  }>({ checked: false, isLoggedIn: false, user: null });

  // Check auth on mount and when storage changes
  useEffect(() => {
    const checkAuth = () => {
      const { isLoggedIn, user } = getAuthFromStorage();
      setAuthState({ checked: true, isLoggedIn, user });
    };
    
    // Check immediately
    checkAuth();
    
    // Listen for storage changes (cross-tab sync)
    window.addEventListener("storage", checkAuth);
    
    // Also check periodically for same-tab changes
    const interval = setInterval(checkAuth, 500);
    
    return () => {
      window.removeEventListener("storage", checkAuth);
      clearInterval(interval);
    };
  }, []);

  // Close menu on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navItems = [
    { href: "/orders", label: "سفارشات من", icon: Package },
    { href: "/new-order", label: "سفارش جدید", icon: ShoppingCart },
  ];

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setAuthState({ checked: true, isLoggedIn: false, user: null });
    window.location.href = "/login";
  };

  const { checked, isLoggedIn, user } = authState;
  const isUserAdmin = user?.is_admin ?? false;
  const userName = user?.full_name || user?.first_name || "کاربر";

  return (
    <header className="sticky top-0 z-40 bg-surface border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Right side - Logo and mobile menu */}
          <div className="flex items-center gap-4">
            {onMenuToggle && (
              <button
                onClick={onMenuToggle}
                className="lg:hidden p-2 hover:bg-accent rounded-lg transition-colors"
                aria-label={isSidebarOpen ? "بستن منو" : "باز کردن منو"}
              >
                {isSidebarOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>
            )}

            <Link href="/" className="flex items-center gap-2">
              <Image
                src="/images/logo.png"
                alt="Sheetaro"
                width={40}
                height={40}
                className="rounded-lg"
              />
              <span className="text-xl font-bold text-primary hidden sm:block">
                شیتارو
              </span>
            </Link>
          </div>

          {/* Center - Navigation (Desktop) - Only show when logged in */}
          {isLoggedIn && (
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "bg-primary-50 text-primary"
                      : "text-muted hover:bg-accent hover:text-foreground"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              ))}
              {isUserAdmin && (
                <Link
                  href="/admin"
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    pathname.startsWith("/admin")
                      ? "bg-primary-50 text-primary"
                      : "text-muted hover:bg-accent hover:text-foreground"
                  )}
                >
                  <Settings className="w-4 h-4" />
                  پنل مدیریت
                </Link>
              )}
            </nav>
          )}

          {/* Left side - User menu or auth buttons */}
          <div className="flex items-center gap-2">
            {!checked ? (
              // Loading state - show skeleton while checking auth
              <div className="flex items-center gap-2 animate-pulse">
                <div className="w-8 h-8 rounded-full bg-accent" />
                <div className="hidden sm:block w-16 h-4 rounded bg-accent" />
              </div>
            ) : isLoggedIn ? (
              // Logged in - show user menu
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-2 hover:bg-accent rounded-lg transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <User className="w-4 h-4 text-primary" />
                  </div>
                  <span className="hidden sm:block text-sm font-medium">
                    {userName}
                  </span>
                </button>

                {/* Dropdown menu */}
                {userMenuOpen && (
                  <div className="absolute left-0 top-full mt-2 w-48 bg-surface rounded-xl shadow-medium border border-border py-2 animate-slide-down">
                    <Link
                      href="/profile"
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-accent transition-colors"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      پروفایل
                    </Link>
                    <Link
                      href="/orders"
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-accent transition-colors"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Package className="w-4 h-4" />
                      سفارشات من
                    </Link>
                    <hr className="my-2 border-border" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 px-4 py-2 text-sm text-danger hover:bg-danger-light w-full transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      خروج
                    </button>
                  </div>
                )}
              </div>
            ) : (
              // Not logged in - show auth buttons
              <>
                <Link 
                  href="/login"
                  className="inline-flex items-center justify-center font-medium rounded-lg transition-all h-9 px-3 text-sm bg-transparent text-foreground hover:bg-accent"
                >
                  ورود
                </Link>
                <Link 
                  href="/register"
                  className="inline-flex items-center justify-center font-medium rounded-lg transition-all h-9 px-3 text-sm bg-primary text-white hover:bg-primary-800"
                >
                  ثبت‌نام
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
