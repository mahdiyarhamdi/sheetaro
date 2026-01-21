"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui";
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
import { isAuthenticated, isAdmin, logout, getUser } from "@/lib/auth";

interface HeaderProps {
  onMenuToggle?: () => void;
  isSidebarOpen?: boolean;
}

export function Header({ onMenuToggle, isSidebarOpen }: HeaderProps) {
  const pathname = usePathname();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isUserAdmin, setIsUserAdmin] = useState(false);
  const [userName, setUserName] = useState("");
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsLoggedIn(isAuthenticated());
    setIsUserAdmin(isAdmin());
    const user = getUser();
    if (user) {
      setUserName(user.full_name || "کاربر");
    }
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
    logout();
  };

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

          {/* Center - Navigation (Desktop) */}
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
            {isLoggedIn ? (
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
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    ورود
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant="primary" size="sm">
                    ثبت‌نام
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

