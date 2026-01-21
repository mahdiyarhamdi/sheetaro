"use client";

import { useQuery } from "@tanstack/react-query";
import { catalogApi, plansApi, Category, Attribute, DesignPlan, Template, Questionnaire } from "@/lib/api";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const response = await catalogApi.getCategories();
      return response.data.items;
    },
  });
}

export function useCategory(categoryId: string) {
  return useQuery({
    queryKey: ["category", categoryId],
    queryFn: async () => {
      const response = await catalogApi.getCategory(categoryId);
      return response.data;
    },
    enabled: !!categoryId,
  });
}

export function useCategoryAttributes(categoryId: string) {
  return useQuery({
    queryKey: ["categoryAttributes", categoryId],
    queryFn: async () => {
      const response = await catalogApi.getCategoryAttributes(categoryId);
      return response.data.items;
    },
    enabled: !!categoryId,
  });
}

export function useCategoryPlans(categoryId: string) {
  return useQuery({
    queryKey: ["categoryPlans", categoryId],
    queryFn: async () => {
      const response = await catalogApi.getCategoryPlans(categoryId);
      return response.data.items;
    },
    enabled: !!categoryId,
  });
}

export function usePlan(planId: string) {
  return useQuery({
    queryKey: ["plan", planId],
    queryFn: async () => {
      const response = await plansApi.getPlan(planId);
      return response.data;
    },
    enabled: !!planId,
  });
}

export function usePlanTemplates(planId: string) {
  return useQuery({
    queryKey: ["planTemplates", planId],
    queryFn: async () => {
      const response = await plansApi.getPlanTemplates(planId);
      return response.data.items;
    },
    enabled: !!planId,
  });
}

export function usePlanQuestionnaire(planId: string) {
  return useQuery({
    queryKey: ["planQuestionnaire", planId],
    queryFn: async () => {
      const response = await plansApi.getPlanQuestionnaire(planId);
      return response.data;
    },
    enabled: !!planId,
  });
}

