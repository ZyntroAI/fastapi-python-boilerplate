import { beforeEach, describe, expect, it, vi } from "vitest";
import request from "supertest";

// The service layer is mocked so the HTTP contract is tested without a database.
vi.mock("./services/product.service.js", () => ({
  listProducts: vi.fn(),
  getProduct: vi.fn(),
  createProduct: vi.fn(),
  updateProduct: vi.fn(),
  deleteProduct: vi.fn(),
}));

const service = await import("./services/product.service.js");
const { createApp } = await import("./app.js");

const app = createApp();

const sample = {
  id: "p_1",
  name: "Torque Wrench",
  sku: "TW-100",
  description: null,
  price: 49.99,
  stock: 12,
  status: "ACTIVE",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
};

beforeEach(() => vi.clearAllMocks());

describe("GET /health", () => {
  it("responds ok", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });
});

describe("GET /api/products", () => {
  it("returns items and pagination meta", async () => {
    vi.mocked(service.listProducts).mockResolvedValue({
      items: [sample],
      meta: { page: 1, pageSize: 20, total: 1, totalPages: 1, hasNext: false, hasPrev: false },
    });
    const res = await request(app).get("/api/products?page=1&search=wrench");
    expect(res.status).toBe(200);
    expect(res.body.items).toHaveLength(1);
    expect(res.body.meta.total).toBe(1);
    expect(service.listProducts).toHaveBeenCalledWith(
      expect.objectContaining({ page: 1, search: "wrench" }),
    );
  });

  it("rejects an invalid pageSize with a structured 400", async () => {
    const res = await request(app).get("/api/products?pageSize=999");
    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe("BAD_REQUEST");
    expect(service.listProducts).not.toHaveBeenCalled();
  });
});

describe("POST /api/products", () => {
  it("creates and returns 201", async () => {
    vi.mocked(service.createProduct).mockResolvedValue(sample as never);
    const res = await request(app)
      .post("/api/products")
      .send({ name: "Torque Wrench", sku: "TW-100", price: 49.99, stock: 12, status: "ACTIVE" });
    expect(res.status).toBe(201);
    expect(res.body.id).toBe("p_1");
  });

  it("rejects an invalid body with a structured 400", async () => {
    const res = await request(app).post("/api/products").send({ name: "", sku: "TW 100", price: -5 });
    expect(res.status).toBe(400);
    expect(res.body.error.details.fieldErrors).toBeDefined();
    expect(service.createProduct).not.toHaveBeenCalled();
  });
});

describe("PUT /api/products/:id", () => {
  it("updates and returns the product", async () => {
    vi.mocked(service.updateProduct).mockResolvedValue({ ...sample, stock: 5 } as never);
    const res = await request(app).put("/api/products/p_1").send({ stock: 5 });
    expect(res.status).toBe(200);
    expect(res.body.stock).toBe(5);
  });

  it("surfaces a 404 from the service", async () => {
    const { notFound } = await import("./lib/errors.js");
    vi.mocked(service.updateProduct).mockRejectedValue(notFound("Product p_x not found"));
    const res = await request(app).put("/api/products/p_x").send({ stock: 5 });
    expect(res.status).toBe(404);
    expect(res.body.error.code).toBe("NOT_FOUND");
  });
});

describe("DELETE /api/products/:id", () => {
  it("deletes and returns the id", async () => {
    vi.mocked(service.deleteProduct).mockResolvedValue({ id: "p_1" });
    const res = await request(app).delete("/api/products/p_1");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ id: "p_1" });
  });
});

describe("unknown route", () => {
  it("returns a structured 404", async () => {
    const res = await request(app).get("/api/nope");
    expect(res.status).toBe(404);
    expect(res.body.error.code).toBe("NOT_FOUND");
  });
});
