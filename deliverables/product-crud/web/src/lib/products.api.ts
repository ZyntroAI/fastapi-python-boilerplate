import { apiRequest } from "./api";
import {
  productListResponseSchema,
  productSchema,
  type ListProductsParams,
  type Product,
  type ProductFormValues,
  type ProductListResponse,
} from "../types/product";

/** Serialises list params into a query string; empty values are dropped by the client. */
function toQueryParams(params: ListProductsParams) {
  return {
    page: params.page,
    pageSize: params.pageSize,
    search: params.search.trim() || undefined,
    status: params.status,
    sortBy: params.sortBy,
    sortDir: params.sortDir,
  };
}

export async function fetchProducts(
  params: ListProductsParams,
  signal?: AbortSignal,
): Promise<ProductListResponse> {
  const data = await apiRequest<unknown>("/api/products", {
    params: toQueryParams(params),
    signal,
  });
  return productListResponseSchema.parse(data);
}

export async function fetchProduct(id: string): Promise<Product> {
  const data = await apiRequest<unknown>(`/api/products/${id}`);
  return productSchema.parse(data);
}

export async function createProduct(values: ProductFormValues): Promise<Product> {
  const data = await apiRequest<unknown>("/api/products", { method: "POST", body: values });
  return productSchema.parse(data);
}

export async function updateProduct(id: string, values: Partial<ProductFormValues>): Promise<Product> {
  const data = await apiRequest<unknown>(`/api/products/${id}`, { method: "PUT", body: values });
  return productSchema.parse(data);
}

export async function deleteProduct(id: string): Promise<{ id: string }> {
  return apiRequest<{ id: string }>(`/api/products/${id}`, { method: "DELETE" });
}
