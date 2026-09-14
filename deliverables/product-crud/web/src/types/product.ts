import { z } from "zod";

/**
 * Frontend mirror of `server/src/lib/zod/product.schema.ts`.
 * Keep the field names, enums and constraints in sync with the server.
 */

export const PRODUCT_STATUSES = ["DRAFT", "ACTIVE", "ARCHIVED"] as const;
export const productStatusSchema = z.enum(PRODUCT_STATUSES);
export type ProductStatus = z.infer<typeof productStatusSchema>;

export const PRODUCT_STATUS_LABEL: Record<ProductStatus, string> = {
  DRAFT: "Draft",
  ACTIVE: "Active",
  ARCHIVED: "Archived",
};

/** Shape returned by the API (Decimal → number, Date → ISO string). */
export const productSchema = z.object({
  id: z.string(),
  name: z.string(),
  sku: z.string(),
  description: z.string().nullable(),
  price: z.number(),
  stock: z.number(),
  status: productStatusSchema,
  createdAt: z.string(),
  updatedAt: z.string(),
});
export type Product = z.infer<typeof productSchema>;

export const paginationMetaSchema = z.object({
  page: z.number(),
  pageSize: z.number(),
  total: z.number(),
  totalPages: z.number(),
  hasNext: z.boolean(),
  hasPrev: z.boolean(),
});
export type PaginationMeta = z.infer<typeof paginationMetaSchema>;

export const productListResponseSchema = z.object({
  items: z.array(productSchema),
  meta: paginationMetaSchema,
});
export type ProductListResponse = z.infer<typeof productListResponseSchema>;

/** Form contract — validated client-side with the same rules as the server. */
export const productFormSchema = z.object({
  name: z.string().trim().min(1, "กรุณากรอกชื่อสินค้า").max(200),
  sku: z
    .string()
    .trim()
    .min(1, "กรุณากรอก SKU")
    .max(64)
    .regex(/^[A-Za-z0-9._-]+$/, "SKU ใช้ได้เฉพาะตัวอักษร ตัวเลข . - _"),
  description: z.string().trim().max(2000).optional().or(z.literal("")),
  price: z.coerce
    .number({ invalid_type_error: "ราคาต้องเป็นตัวเลข" })
    .nonnegative("ราคาต้องไม่ติดลบ")
    .refine((v) => Math.abs(v * 100 - Math.round(v * 100)) < 1e-9, "ราคาทศนิยมไม่เกิน 2 ตำแหน่ง"),
  stock: z.coerce.number().int("จำนวนต้องเป็นจำนวนเต็ม").nonnegative("จำนวนต้องไม่ติดลบ"),
  status: productStatusSchema,
});
export type ProductFormValues = z.infer<typeof productFormSchema>;

export interface ListProductsParams {
  page: number;
  pageSize: number;
  search: string;
  status?: ProductStatus;
  sortBy?: "name" | "price" | "stock" | "createdAt" | "updatedAt";
  sortDir?: "asc" | "desc";
}

export const DEFAULT_LIST_PARAMS: ListProductsParams = {
  page: 1,
  pageSize: 20,
  search: "",
  sortBy: "createdAt",
  sortDir: "desc",
};
