import { describe, expect, it } from "vitest";
import {
  createProductSchema,
  listProductsQuerySchema,
  updateProductSchema,
} from "./product.schema.js";

const valid = {
  name: "Torque Wrench",
  sku: "TW-100",
  price: 49.99,
  stock: 12,
  status: "ACTIVE" as const,
};

describe("createProductSchema", () => {
  it("accepts a valid payload and applies defaults", () => {
    const parsed = createProductSchema.parse({ name: "Bolt", sku: "B-1", price: 1.5 });
    expect(parsed.stock).toBe(0);
    expect(parsed.status).toBe("DRAFT");
  });

  it("rejects a negative price", () => {
    expect(() => createProductSchema.parse({ ...valid, price: -1 })).toThrow();
  });

  it("rejects more than 2 decimal places", () => {
    expect(() => createProductSchema.parse({ ...valid, price: 1.999 })).toThrow();
  });

  it("rejects a sku with spaces", () => {
    expect(() => createProductSchema.parse({ ...valid, sku: "TW 100" })).toThrow();
  });

  it("rejects a non-integer stock", () => {
    expect(() => createProductSchema.parse({ ...valid, stock: 1.5 })).toThrow();
  });

  it("trims name and sku", () => {
    const parsed = createProductSchema.parse({ ...valid, name: "  Bolt  ", sku: "  B-1  " });
    expect(parsed.name).toBe("Bolt");
    expect(parsed.sku).toBe("B-1");
  });
});

describe("updateProductSchema", () => {
  it("accepts a partial payload", () => {
    expect(updateProductSchema.parse({ stock: 3 })).toEqual({ stock: 3 });
  });

  it("accepts an empty payload", () => {
    expect(updateProductSchema.parse({})).toEqual({});
  });
});

describe("listProductsQuerySchema", () => {
  it("applies defaults and coerces strings from the query string", () => {
    const parsed = listProductsQuerySchema.parse({ page: "2", pageSize: "50" });
    expect(parsed).toMatchObject({ page: 2, pageSize: 50, sortBy: "createdAt", sortDir: "desc" });
  });

  it("rejects a pageSize above the cap", () => {
    expect(() => listProductsQuerySchema.parse({ pageSize: "1000" })).toThrow();
  });

  it("rejects an unknown status", () => {
    expect(() => listProductsQuerySchema.parse({ status: "GONE" })).toThrow();
  });
});
