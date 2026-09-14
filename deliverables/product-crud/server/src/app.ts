import cors from "cors";
import express, { type NextFunction, type Request, type Response } from "express";
import { ZodError } from "zod";
import { HttpError } from "./lib/errors.js";
import productRoutes from "./routes/product.routes.js";

export function createApp() {
  const app = express();

  app.use(
    cors({
      origin: process.env.CORS_ORIGIN?.split(",").map((o) => o.trim()) ?? true,
      credentials: true,
    }),
  );
  app.use(express.json({ limit: "1mb" }));

  app.get("/health", (_req, res) => res.json({ status: "ok" }));
  app.use("/api/products", productRoutes);

  app.use((_req, res) => res.status(404).json({ error: { code: "NOT_FOUND", message: "Route not found" } }));

  // Central error handler: HttpError and ZodError map to structured payloads.
  app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (error instanceof HttpError) {
      return res
        .status(error.status)
        .json({ error: { code: error.code, message: error.message, details: error.details } });
    }
    if (error instanceof ZodError) {
      return res
        .status(400)
        .json({ error: { code: "BAD_REQUEST", message: "Validation failed", details: error.flatten() } });
    }
    console.error("[unhandled]", error);
    return res.status(500).json({ error: { code: "INTERNAL", message: "Internal server error" } });
  });

  return app;
}
