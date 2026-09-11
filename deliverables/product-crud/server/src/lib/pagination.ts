import type { ListProductsQuery } from "../lib/zod/product.schema.js";
import { SORTABLE_FIELDS } from "../lib/zod/product.schema.js";

export interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export const DEFAULT_PAGE_SIZE = 20;

export function buildPaginationMeta(page: number, pageSize: number, total: number): PaginationMeta {
  const totalPages = total === 0 ? 0 : Math.ceil(total / pageSize);
  return {
    page,
    pageSize,
    total,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1 && totalPages > 0,
  };
}

export function toPrismaSkipTake(query: Pick<ListProductsQuery, "page" | "pageSize">) {
  const pageSize = query.pageSize ?? DEFAULT_PAGE_SIZE;
  const page = query.page ?? 1;
  return { skip: (page - 1) * pageSize, take: pageSize };
}

type SortField = (typeof SORTABLE_FIELDS)[number];

export function toPrismaOrderBy(sortBy: SortField, sortDir: "asc" | "desc") {
  return { [sortBy]: sortDir } as Record<SortField, "asc" | "desc">;
}

/** Builds the Prisma `where` clause for the list endpoint. Pure — safe to unit test. */
export function buildProductWhere(query: Pick<ListProductsQuery, "search" | "status">) {
  const where: Record<string, unknown> = {};
  if (query.status) where.status = query.status;
  const term = query.search?.trim();
  if (term) {
    where.OR = [
      { name: { contains: term, mode: "insensitive" } },
      { sku: { contains: term, mode: "insensitive" } },
      { description: { contains: term, mode: "insensitive" } },
    ];
  }
  return where;
}
