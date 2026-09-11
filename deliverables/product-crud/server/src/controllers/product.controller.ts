import type { NextFunction, Request, Response } from "express";
import { ZodError } from "zod";
import { badRequest } from "../lib/errors.js";
import {
  createProductSchema,
  listProductsQuerySchema,
  productIdSchema,
  updateProductSchema,
} from "../lib/zod/product.schema.js";
import * as productService from "../services/product.service.js";

function parse<T>(schema: { parse: (v: unknown) => T }, value: unknown): T {
  try {
    return schema.parse(value);
  } catch (error) {
    if (error instanceof ZodError) {
      throw badRequest("Validation failed", error.flatten());
    }
    throw error;
  }
}

export async function list(req: Request, res: Response, next: NextFunction) {
  try {
    const query = parse(listProductsQuerySchema, req.query);
    const result = await productService.listProducts(query);
    res.json(result);
  } catch (error) {
    next(error);
  }
}

export async function getById(req: Request, res: Response, next: NextFunction) {
  try {
    const { id } = parse(productIdSchema, req.params);
    res.json(await productService.getProduct(id));
  } catch (error) {
    next(error);
  }
}

export async function create(req: Request, res: Response, next: NextFunction) {
  try {
    const input = parse(createProductSchema, req.body);
    res.status(201).json(await productService.createProduct(input));
  } catch (error) {
    next(error);
  }
}

export async function update(req: Request, res: Response, next: NextFunction) {
  try {
    const { id } = parse(productIdSchema, req.params);
    const input = parse(updateProductSchema, req.body);
    res.json(await productService.updateProduct(id, input));
  } catch (error) {
    next(error);
  }
}

export async function remove(req: Request, res: Response, next: NextFunction) {
  try {
    const { id } = parse(productIdSchema, req.params);
    res.json(await productService.deleteProduct(id));
  } catch (error) {
    next(error);
  }
}
