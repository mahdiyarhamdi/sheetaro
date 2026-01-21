"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
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
  isAuthenticated as checkIsAuthenticated,
} from "@/lib/auth";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();

  // Get current user query
  const {
    data: user,
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
        return null;
      }
    },
    enabled: checkIsAuthenticated(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setTokens(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      queryClient.setQueryData(["currentUser"], response.data.user);
      toast.success("ثبت‌نام با موفقیت انجام شد!");
      router.push("/");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response, _, context) => {
      setTokens(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      queryClient.setQueryData(["currentUser"], response.data.user);
      toast.success("ورود موفقیت‌آمیز بود!");
      
      // Redirect to stored path or home
      const searchParams = new URLSearchParams(window.location.search);
      const redirect = searchParams.get("redirect") || "/";
      router.push(redirect);
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
  const logout = () => {
    clearTokens();
    queryClient.clear();
    toast.success("با موفقیت خارج شدید");
    router.push("/login");
  };

  return {
    user,
    isLoadingUser,
    isAuthenticated: !!user,
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

