import { z } from "zod"

export const maxDuration = 120

const requestSchema = z.object({
  message: z.string().trim().min(1),
  conversation_id: z.string().min(1).max(200),
})

export async function POST(req: Request) {
  const parsed = requestSchema.safeParse(await req.json().catch(() => null))
  if (!parsed.success) {
    return new Response("Invalid chat request.", { status: 400 })
  }
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000"
  try {
    const response = await fetch(
      `${backend.replace(/\/$/, "")}/v1/chat/stream`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed.data),
        signal: req.signal,
        cache: "no-store",
      }
    )
    if (!response.ok) {
      const data = await response.json().catch(() => null)
      return new Response(
        typeof data?.detail === "string"
          ? data.detail
          : "Chat backend request failed.",
        { status: response.status }
      )
    }
    if (
      !response.body ||
      !response.headers.get("content-type")?.includes("text/event-stream")
    ) {
      return new Response("Invalid chat backend stream.", { status: 502 })
    }
    // Forward bytes as they arrive; never buffer the model's entire reply.
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
      },
    })
  } catch {
    return new Response("Could not reach the chat backend.", { status: 502 })
  }
}
