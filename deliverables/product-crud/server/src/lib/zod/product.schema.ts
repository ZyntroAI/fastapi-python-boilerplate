import { z } from "zod";

/**
 * Single source of truth for the Product contract on the server.
 * The frontend mirrors the output shape in src/types/product.ts.
 */

export const PRODUCT_STATUSES = ["DRAFT", "ACTIVE", "ARCHIVED"] as const;

export const productStatusSchema = z.enum(PRODUCT_STATUSES);

const priceSchema = z
  .number({ invalid_type_error: "price must be a number" })
  .nonnegative("price must be zero or greater")
  .max(9_999_999.99, "price exceeds maximum supported value")
  .refine(
    (v) => Number.isInteger(Math.round(v * 100)) && Math.abs(v * 100 - Math.round(v * 100)) < 1e-9,
    "price supports at most 2 decimal places",
  );

export const createProductSchema = z.object({
  name: z.string().trim().min(1, "name is required").max(200),
  sku: z
    .string()
    .trim()
    .min(1, "sku is required")
    .max(64)
    .regex(/^[A-Za-z0-9._-]+$/, "sku may only contain letters, numbers, dot, dash and underscore"),
  description: z.string().trim().max(2000).nullish().or(z.literal("")),
  price: priceSchema,
  stock: z.number().int("stock must be an integer").nonnegative().default(0),
  status: productStatusSchema.default("DRAFT"),
});

export const updateProductSchema = createProductSchema.partial();

export const productIdSchema = z.object({
  id: z.string().trim().min(1, "id is required").max(64),
});

export const SORTABLE_FIELDS = ["name", "price", "stock", "createdAt", "updatedAt"] as const;

export const listProductsQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().trim().max(200).optional(),
  status: productStatusSchema.optional(),
  sortBy: z.enum(SORTABLE_FIELDS).default("createdAt"),
  sortDir: z.enum(["asc", "desc"]).default("desc"),
});

export type CreateProductInput = z.infer<typeof createProductSchema>;
export type UpdateProductInput = z.infer<typeof updateProductSchema>;
export type ListProductsQuery = z.infer<typeof listProductsQuerySchema>;
