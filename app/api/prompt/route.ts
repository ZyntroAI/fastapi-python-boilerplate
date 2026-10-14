
import { NextResponse } from "next/server";
import { z } from "zod";

const PromptSchema = z.object({
  prompt: z.string().trim().min(1).max(100_000),
});

export async function POST(request: Request) {
  try {
    const body: unknown = await request.json();
    const result = PromptSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        {
          error: "VALIDATION_ERROR",
          message: "Invalid prompt input",
          details: result.error.issues,
        },
        { status: 422 },
      );
    }

    return NextResponse.json({
      status: "accepted",
      length: result.data.prompt.length,
    });
  } catch {
    return NextResponse.json(
      {
        error: "BAD_REQUEST",
        message: "Invalid JSON request body",
      },
      { status: 400 },
    );
  }
}
