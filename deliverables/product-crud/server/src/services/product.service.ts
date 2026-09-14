import type { Prisma } from "@prisma/client";
import { prisma } from "../lib/prisma.js";
import { conflict, notFound } from "../lib/errors.js";
import {
  buildPaginationMeta,
  buildProductWhere,
  toPrismaOrderBy,
  toPrismaSkipTake,
} from "../lib/pagination.js";
import type { PaginationMeta } from "../lib/pagination.js";
import type {
  CreateProductInput,
  ListProductsQuery,
  UpdateProductInput,
} from "../lib/zod/product.schema.js";

export interface ProductDto {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  price: number;
  stock: number;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProductListResult {
  items: ProductDto[];
  meta: PaginationMeta;
}

interface ProductRow {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  price: { toNumber(): number } | number;
  stock: number;
  status: string;
  createdAt: Date;
  updatedAt: Date;
}

/** Normalises a Prisma row (Decimal → number, Date → ISO string) for the API surface. */
export function toProductDto(row: ProductRow): ProductDto {
  return {
    id: row.id,
    name: row.name,
    sku: row.sku,
    description: row.description,
    price: typeof row.price === "number" ? row.price : row.price.toNumber(),
    stock: row.stock,
    status: row.status,
    createdAt: row.createdAt.toISOString(),
    updatedAt: row.updatedAt.toISOString(),
  };
}

function describeUniqueError(error: unknown): string | null {
  const e = error as { code?: string; meta?: { target?: string[] } };
  if (e?.code !== "P2002") return null;
  const target = e.meta?.target?.join(", ") ?? "field";
  return `A product with this ${target} already exists`;
}

export async function listProducts(query: ListProductsQuery): Promise<ProductListResult> {
  const where = buildProductWhere(query) as Prisma.ProductWhereInput;
  const { skip, take } = toPrismaSkipTake(query);
  const orderBy = toPrismaOrderBy(query.sortBy, query.sortDir) as Prisma.ProductOrderByWithRelationInput;

  const [rows, total] = await Promise.all([
    prisma.product.findMany({ where, skip, take, orderBy }),
    prisma.product.count({ where }),
  ]);

  return {
    items: rows.map((r) => toProductDto(r as unknown as ProductRow)),
    meta: buildPaginationMeta(query.page, take, total),
  };
}

export async function getProduct(id: string): Promise<ProductDto> {
  const row = await prisma.product.findUnique({ where: { id } });
  if (!row) throw notFound(`Product ${id} not found`);
  return toProductDto(row as unknown as ProductRow);
}

export async function createProduct(input: CreateProductInput): Promise<ProductDto> {
  try {
    const row = await prisma.product.create({
      data: {
        name: input.name,
        sku: input.sku,
        description: input.description || null,
        price: input.price,
        stock: input.stock ?? 0,
        status: input.status ?? "DRAFT",
      },
    });
    return toProductDto(row as unknown as ProductRow);
  } catch (error) {
    const message = describeUniqueError(error);
    if (message) throw conflict(message);
    throw error;
  }
}

export async function updateProduct(id: string, input: UpdateProductInput): Promise<ProductDto> {
  await getProduct(id);
  try {
    const row = await prisma.product.update({
      where: { id },
      data: {
        ...(input.name !== undefined ? { name: input.name } : {}),
        ...(input.sku !== undefined ? { sku: input.sku } : {}),
        ...(input.description !== undefined ? { description: input.description || null } : {}),
        ...(input.price !== undefined ? { price: input.price } : {}),
        ...(input.stock !== undefined ? { stock: input.stock } : {}),
        ...(input.status !== undefined ? { status: input.status } : {}),
      },
    });
    return toProductDto(row as unknown as ProductRow);
  } catch (error) {
    const message = describeUniqueError(error);
    if (message) throw conflict(message);
    throw error;
  }
}

export async function deleteProduct(id: string): Promise<{ id: string }> {
  await getProduct(id);
  await prisma.product.delete({ where: { id } });
  return { id };
}
