"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  ordersApi,
  getErrorMessage,
  Order,
  CreateOrderRequest,
} from "@/lib/api";

interface UseOrdersOptions {
  page?: number;
  pageSize?: number;
  status?: string;
}

export function useOrders(options: UseOrdersOptions = {}) {
  const { page = 1, pageSize = 10, status } = options;
  const queryClient = useQueryClient();

  // List orders
  const {
    data: ordersData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["orders", { page, pageSize, status }],
    queryFn: async () => {
      const response = await ordersApi.list({
        page,
        page_size: pageSize,
        status,
      });
      return response.data;
    },
  });

  // Get single order
  const getOrder = (orderId: string) => {
    return useQuery({
      queryKey: ["order", orderId],
      queryFn: async () => {
        const response = await ordersApi.get(orderId);
        return response.data;
      },
      enabled: !!orderId,
    });
  };

  // Create order mutation
  const createOrderMutation = useMutation({
    mutationFn: ({ data, userId }: { data: CreateOrderRequest; userId: string }) => 
      ordersApi.create(data, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      toast.success("سفارش با موفقیت ایجاد شد!");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  return {
    orders: ordersData?.items ?? [],
    total: ordersData?.total ?? 0,
    page: ordersData?.page ?? 1,
    pageSize: ordersData?.page_size ?? 10,
    isLoading,
    error,
    refetch,
    
    getOrder,
    
    createOrder: createOrderMutation.mutate,
    isCreatingOrder: createOrderMutation.isPending,
  };
}

export function useOrder(orderId: string) {
  return useQuery({
    queryKey: ["order", orderId],
    queryFn: async () => {
      const response = await ordersApi.get(orderId);
      return response.data;
    },
    enabled: !!orderId,
  });
}

