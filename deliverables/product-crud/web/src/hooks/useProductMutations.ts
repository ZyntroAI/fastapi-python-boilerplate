import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createProduct, deleteProduct, updateProduct } from "../lib/products.api";
import type { Product, ProductFormValues } from "../types/product";
import { productKeys } from "./queryKeys";

interface MutationCallbacks<TData> {
  onSuccess?: (data: TData) => void;
  onError?: (error: unknown) => void;
}

/**
 * Create / update / delete in one place so the table (delete) and the modal
 * (create + update) share the same invalidation logic instead of duplicating it.
 */
export function useProductMutations(callbacks: MutationCallbacks<Product | { id: string }> = {}) {
  const queryClient = useQueryClient();

  const invalidateLists = () => queryClient.invalidateQueries({ queryKey: productKeys.lists() });

  const create = useMutation({
    mutationFn: (values: ProductFormValues) => createProduct(values),
    onSuccess: (data) => {
      void invalidateLists();
      callbacks.onSuccess?.(data);
    },
    onError: (error) => callbacks.onError?.(error),
  });

  const update = useMutation({
    mutationFn: ({ id, values }: { id: string; values: Partial<ProductFormValues> }) =>
      updateProduct(id, values),
    onSuccess: (data) => {
      queryClient.setQueryData(productKeys.detail(data.id), data);
      void invalidateLists();
      callbacks.onSuccess?.(data);
    },
    onError: (error) => callbacks.onError?.(error),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteProduct(id),
    onSuccess: (data) => {
      queryClient.removeQueries({ queryKey: productKeys.detail(data.id) });
      void invalidateLists();
      callbacks.onSuccess?.(data);
    },
    onError: (error) => callbacks.onError?.(error),
  });

  return {
    create,
    update,
    remove,
    isMutating: create.isPending || update.isPending || remove.isPending,
  };
}
