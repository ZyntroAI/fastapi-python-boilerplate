export class HttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code = "ERROR",
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "HttpError";
  }
}

export const badRequest = (message: string, details?: unknown) =>
  new HttpError(400, message, "BAD_REQUEST", details);

export const notFound = (message = "Resource not found") => new HttpError(404, message, "NOT_FOUND");

export const conflict = (message: string, details?: unknown) =>
  new HttpError(409, message, "CONFLICT", details);
