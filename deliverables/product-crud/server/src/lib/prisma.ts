import { PrismaClient } from "@prisma/client";

/**
 * A single PrismaClient for the process. In development the instance is cached
 * on globalThis so hot-reload does not open a new pool on every reload.
 */
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["warn", "error"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
