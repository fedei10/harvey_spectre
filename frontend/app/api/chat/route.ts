import { z } from "zod"

export const maxDuration = 120

const requestSchema = z.object({
  id: z.string().min(1).max(200),
  trigger: z.enum(["submit-message", "regenerate-message"]).optional(),
  messages: z
    .array(
      z.object({
        role: z.enum(["user", "assistant", "system"]),
        parts: z.array(
          z.object({
            type: z.string(),
            text: z.string().optional(),
          })
        ),
      })
    )
    .min(1),
})

export async function POST(req: Request) {
  const parsed = requestSchema.safeParse(await req.json().catch(() => null))
  if (!parsed.success) {
    return new Response("Invalid chat request.", { status: 400 })
  }
  const { id, messages, trigger } = parsed.data
  if (trigger === "regenerate-message") {
    return new Response("Start a new message to continue this conversation.", {
      status: 400,
    })
  }
  const latest = messages.at(-1)!
  const message = latest.parts
    .filter((part) => part.type === "text")
    .map((part) => part.text ?? "")
    .join("\n")
    .trim()
  if (latest.role !== "user" || !message) {
    return new Response("A user message is required.", { status: 400 })
  }

  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000"
  try {
    const response = await fetch(
      `${backend.replace(/\/$/, "")}/v1/chat/stream`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, conversation_id: id }),
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
        "x-vercel-ai-ui-message-stream": "v1",
        "X-Accel-Buffering": "no",
      },
    })
  } catch {
    return new Response("Could not reach the chat backend.", { status: 502 })
  }
}
