"use client";

import { authApi, User } from "./api";

const TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user";

/**
 * Stores authentication tokens in localStorage
 */
export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

/**
 * Gets the access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Gets the refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Removes all auth tokens from localStorage
 */
export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Stores user data in localStorage
 */
export function setUser(user: User): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Gets user data from localStorage
 */
export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Checks if the user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

/**
 * Checks if the user is an admin
 */
export function isAdmin(): boolean {
  const user = getUser();
  return user?.is_admin ?? false;
}

/**
 * Logs out the user
 */
export function logout(): void {
  clearTokens();
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

/**
 * Fetches and updates user data from API
 */
export async function refreshUserData(): Promise<User | null> {
  try {
    const response = await authApi.me();
    setUser(response.data);
    return response.data;
  } catch {
    return null;
  }
}

