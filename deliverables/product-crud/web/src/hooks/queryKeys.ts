import type { ListProductsParams } from "../types/product";

/**
 * Paging/search/sort are part of the key, so each page + search term gets its
 * own cache entry instead of all views sharing one.
 */
export const productKeys = {
  all: ["products"] as const,
  lists: () => [...productKeys.all, "list"] as const,
  list: (params: ListProductsParams) =>
    [...productKeys.lists(), { ...params, search: params.search.trim() }] as const,
  details: () => [...productKeys.all, "detail"] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
};
