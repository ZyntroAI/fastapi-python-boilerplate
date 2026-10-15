
export class HttpError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "HttpError";
  }
}

export function errorResponse(error: unknown) {
  if (error instanceof HttpError) {
    return Response.json(
      {
        error: error.code,
        message: error.message,
      },
      { status: error.status },
    );
  }

  return Response.json(
    {
      error: "INTERNAL_SERVER_ERROR",
      message: "An unexpected error occurred",
    },
    { status: 500 },
  );
}
