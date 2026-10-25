export type ChatMessage = {
  id: string
  role: "user" | "assistant"
  text: string
  state?: "writing" | "complete" | "stopped" | "error"
}

export type ChatEvent =
  | { type: "start"; conversation_id: string; message_id: string }
  | { type: "delta"; text: string }
  | { type: "error"; message: string }
  | { type: "done" }

function parseEvent(data: string): ChatEvent {
  const event = JSON.parse(data)
  if (
    (event?.type === "start" &&
      typeof event.conversation_id === "string" &&
      typeof event.message_id === "string") ||
    (event?.type === "delta" && typeof event.text === "string") ||
    (event?.type === "error" && typeof event.message === "string") ||
    event?.type === "done"
  )
    return event
  throw new Error("Invalid response from the chat backend.")
}

// Decode bytes incrementally: a network chunk can split an SSE frame or UTF-8 character.
export async function* readChatStream(
  body: ReadableStream<Uint8Array>
): AsyncGenerator<ChatEvent> {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  let data: string[] = []
  try {
    while (true) {
      const { value, done } = await reader.read()
      buffer += decoder.decode(value, { stream: !done })
      let newline: number
      while ((newline = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, newline).replace(/\r$/, "")
        buffer = buffer.slice(newline + 1)
        if (line === "" && data.length) {
          const event = parseEvent(data.join("\n"))
          data = []
          yield event
          if (event.type === "done") return
        } else if (line.startsWith("data:")) {
          data.push(line.slice(5).replace(/^ /, ""))
        }
      }
      if (done)
        throw new Error(
          "The connection ended before the response finished. You can send a follow-up message."
        )
    }
  } finally {
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
