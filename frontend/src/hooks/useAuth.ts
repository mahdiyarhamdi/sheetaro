"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import {
  authApi,
  getErrorMessage,
  LoginRequest,
  RegisterRequest,
  User,
} from "@/lib/api";
import {
  setTokens,
  setUser,
  clearTokens,
  getAccessToken,
  getUser as getStoredUser,
} from "@/lib/auth";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // Track if we're on client and have checked auth
  const [isClient, setIsClient] = useState(false);
  const [initialUser, setInitialUser] = useState<User | null>(null);
  
  // On mount, check localStorage for stored user data
  useEffect(() => {
    setIsClient(true);
    // Get user from localStorage immediately for fast UI update
    const storedUser = getStoredUser();
    if (storedUser) {
      setInitialUser(storedUser);
    }
  }, []);
  
  // Check if we have a token
  const hasToken = isClient && !!getAccessToken();

  // Get current user query - will validate/refresh user from API
  const {
    data: apiUser,
    isLoading: isLoadingUser,
    refetch: refetchUser,
  } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const token = getAccessToken();
      if (!token) return null;
      try {
        const response = await authApi.me();
        setUser(response.data);
        return response.data;
      } catch {
        clearTokens();
        setInitialUser(null);
        return null;
      }
    },
    enabled: hasToken,
    staleTime: 5 * 60 * 1000, // 5 minutes
    initialData: initialUser,
  });
  
  // Use API user if available, otherwise use stored user
  const user = apiUser ?? initialUser;

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setTokens(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      setInitialUser(response.data.user);
      queryClient.setQueryData(["currentUser"], response.data.user);
      toast.success("ثبت‌نام با موفقیت انجام شد!");
      window.location.href = "/";
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setTokens(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      setInitialUser(response.data.user);
      queryClient.setQueryData(["currentUser"], response.data.user);
      toast.success("ورود موفقیت‌آمیز بود!");
      
      // Redirect to stored path or home (use window.location for full page refresh)
      const searchParams = new URLSearchParams(window.location.search);
      const redirect = searchParams.get("redirect") || "/";
      window.location.href = redirect;
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Generate Telegram link OTP
  const generateTelegramLinkMutation = useMutation({
    mutationFn: () => authApi.generateTelegramLink(),
    onSuccess: (response) => {
      toast.success("کد تایید ایجاد شد");
      return response.data;
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Logout function
  const logout = useCallback(() => {
    clearTokens();
    setInitialUser(null);
    queryClient.setQueryData(["currentUser"], null);
    queryClient.clear();
    toast.success("با موفقیت خارج شدید");
    router.push("/login");
  }, [queryClient, router]);

  // Compute auth state
  // Still checking if we haven't confirmed we're on client yet
  const isCheckingAuth = !isClient || (hasToken && isLoadingUser && !initialUser);
  const isAuthenticated = !!user || (hasToken && isLoadingUser);

  return {
    user,
    isLoadingUser: isCheckingAuth,
    isAuthenticated,
    isAdmin: user?.is_admin ?? false,
    
    // Register
    register: registerMutation.mutate,
    isRegistering: registerMutation.isPending,
    
    // Login
    login: loginMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    
    // Telegram link
    generateTelegramLink: generateTelegramLinkMutation.mutate,
    telegramLinkData: generateTelegramLinkMutation.data?.data,
    isGeneratingTelegramLink: generateTelegramLinkMutation.isPending,
    
    // Logout
    logout,
    
    // Refetch
    refetchUser,
  };
}
