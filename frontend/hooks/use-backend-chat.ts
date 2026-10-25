"use client"

import { useEffect, useRef, useState } from "react"
import { readChatStream, type ChatMessage } from "@/lib/chat-stream"

export function useBackendChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<"ready" | "submitted" | "streaming">(
    "ready"
  )
  const [error, setError] = useState<Error>()
  const conversation = useRef<string | null>(null)
  const active = useRef<AbortController | null>(null)

  useEffect(
    () => () => {
      active.current?.abort()
    },
    []
  )

  async function sendMessage(text: string) {
    if (!text.trim() || active.current) return
    const controller = new AbortController()
    active.current = controller
    conversation.current ??= crypto.randomUUID()
    const replyId = crypto.randomUUID()
    let receivedText = false
    const updateReply = (update: Partial<ChatMessage>) =>
      setMessages((previous) =>
        previous.map((message) =>
          message.id === replyId ? { ...message, ...update } : message
        )
      )
    setError(undefined)
    setStatus("submitted")
    setMessages((previous) => [
      ...previous,
      { id: crypto.randomUUID(), role: "user", text: text.trim() },
    ])
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text.trim(),
          conversation_id: conversation.current,
        }),
        signal: controller.signal,
      })
      if (!response.ok)
        throw new Error(
          (await response.text()) ||
            "The chat backend could not complete your request."
        )
      if (
        !response.body ||
        !response.headers.get("content-type")?.includes("text/event-stream")
      ) {
        throw new Error("Invalid response from the chat backend.")
      }
      for await (const event of readChatStream(response.body)) {
        if (controller.signal.aborted) break
        if (event.type === "start") conversation.current = event.conversation_id
        if (event.type === "error") throw new Error(event.message)
        if (event.type === "delta") {
          setStatus("streaming")
          const first = !receivedText
          receivedText = true
          setMessages((previous) =>
            first
              ? [
                  ...previous,
                  {
                    id: replyId,
                    role: "assistant",
                    text: event.text,
                    state: "writing",
                  },
                ]
              : previous.map((message) =>
                  message.id === replyId
                    ? { ...message, text: message.text + event.text }
                    : message
                )
          )
        }
      }
      if (controller.signal.aborted) updateReply({ state: "stopped" })
      else if (!receivedText)
        throw new Error("The backend returned an empty response.")
      else updateReply({ state: "complete" })
    } catch (cause) {
      updateReply({ state: controller.signal.aborted ? "stopped" : "error" })
      if (!controller.signal.aborted)
        setError(
          cause instanceof Error ? cause : new Error("Chat request failed.")
        )
    } finally {
      active.current = null
      setStatus("ready")
    }
  }

  return {
    messages,
    status,
    error,
    sendMessage,
    stop: () => active.current?.abort(),
    clearError: () => setError(undefined),
  }
}
