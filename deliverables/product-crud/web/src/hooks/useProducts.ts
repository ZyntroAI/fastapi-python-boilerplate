import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { fetchProduct, fetchProducts } from "../lib/products.api";
import type { ListProductsParams } from "../types/product";
import { productKeys } from "./queryKeys";

/**
 * Lists products for the given page/search/sort.
 *
 * `placeholderData: keepPreviousData` keeps the previous page on screen while
 * the next one loads, so paging and typing do not flash an empty table.
 */
export function useProducts(params: ListProductsParams) {
  const key = useMemo(() => productKeys.list(params), [params]);

  return useQuery({
    queryKey: key,
    queryFn: ({ signal }) => fetchProducts(params, signal),
    placeholderData: keepPreviousData,
    staleTime: 30_000,
  });
}

export function useProduct(id: string | null) {
  return useQuery({
    queryKey: productKeys.detail(id ?? "none"),
    queryFn: () => fetchProduct(id as string),
    enabled: Boolean(id),
  });
}
