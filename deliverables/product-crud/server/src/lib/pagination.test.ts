import { describe, expect, it } from "vitest";
import {
  buildPaginationMeta,
  buildProductWhere,
  toPrismaOrderBy,
  toPrismaSkipTake,
} from "./pagination.js";

describe("buildPaginationMeta", () => {
  it("computes total pages and flags", () => {
    expect(buildPaginationMeta(1, 20, 45)).toEqual({
      page: 1,
      pageSize: 20,
      total: 45,
      totalPages: 3,
      hasNext: true,
      hasPrev: false,
    });
  });

  it("handles an empty result set", () => {
    const meta = buildPaginationMeta(1, 20, 0);
    expect(meta.totalPages).toBe(0);
    expect(meta.hasNext).toBe(false);
    expect(meta.hasPrev).toBe(false);
  });

  it("marks the last page correctly", () => {
    const meta = buildPaginationMeta(3, 20, 45);
    expect(meta.hasNext).toBe(false);
    expect(meta.hasPrev).toBe(true);
  });
});

describe("toPrismaSkipTake", () => {
  it("maps page 1 to skip 0", () => {
    expect(toPrismaSkipTake({ page: 1, pageSize: 20 })).toEqual({ skip: 0, take: 20 });
  });

  it("maps page 3 to skip 40", () => {
    expect(toPrismaSkipTake({ page: 3, pageSize: 20 })).toEqual({ skip: 40, take: 20 });
  });
});

describe("buildProductWhere", () => {
  it("returns an empty clause with no filters", () => {
    expect(buildProductWhere({})).toEqual({});
  });

  it("adds a case-insensitive OR search across name/sku/description", () => {
    const where = buildProductWhere({ search: "widget" });
    expect(where).toEqual({
      OR: [
        { name: { contains: "widget", mode: "insensitive" } },
        { sku: { contains: "widget", mode: "insensitive" } },
        { description: { contains: "widget", mode: "insensitive" } },
      ],
    });
  });

  it("ignores a whitespace-only search term", () => {
    expect(buildProductWhere({ search: "   " })).toEqual({});
  });

  it("combines status and search", () => {
    const where = buildProductWhere({ status: "ACTIVE", search: "bolt" });
    expect(where.status).toBe("ACTIVE");
    expect(where.OR).toHaveLength(3);
  });
});

describe("toPrismaOrderBy", () => {
  it("builds the order clause", () => {
    expect(toPrismaOrderBy("createdAt", "desc")).toEqual({ createdAt: "desc" });
  });
});
