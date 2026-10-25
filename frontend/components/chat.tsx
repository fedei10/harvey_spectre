"use client"

import type { UIMessage } from "ai"
import { SparklesIcon, XIcon } from "lucide-react"

import {
  Conversation,
  ConversationContent,
  ConversationDownload,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation"
import { Shimmer } from "@/components/ai-elements/shimmer"
import { ChatMessage } from "@/components/chat-message"
import { PromptForm } from "@/components/prompt-form"
import { Suggestions } from "@/components/suggestions"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { useBackendChat } from "@/hooks/use-backend-chat"
import type { ChatMessage as BackendMessage } from "@/lib/chat-stream"

const toUIMessage = (message: BackendMessage): UIMessage => ({
  id: message.id,
  role: message.role,
  parts: [{ type: "text", text: message.text }],
  metadata: message.state,
})

function formatForDownload(message: UIMessage) {
  const text = message.parts
    .map((part) => (part.type === "text" ? part.text : ""))
    .join("")
  const incomplete =
    message.metadata === "stopped" || message.metadata === "error"
  return `## ${message.role === "user" ? "You" : "Harvey"}\n\n${text}${incomplete ? "\n\n_Response incomplete._" : ""}`
}

export function Chat() {
  const { messages, sendMessage, status, stop, error, clearError } =
    useBackendChat()

  const isBusy = status !== "ready"
  const lastMessage = messages.at(-1)

  return (
    <main
      id="main-content"
      className="mx-auto flex min-h-0 w-full flex-1 flex-col"
    >
      <Conversation className="chat-thread min-h-0">
        <ConversationContent className="mx-auto w-full max-w-3xl px-5 py-8 sm:px-8">
          {messages.length === 0 ? (
            <ConversationEmptyState className="chat-welcome min-h-[60svh] gap-6">
              <span className="flex items-center gap-2 text-xs font-medium tracking-[0.2em] text-muted-foreground uppercase">
                <SparklesIcon className="size-3.5" aria-hidden="true" /> Space
                to think
              </span>
              <h1 className="chat-welcome-title">
                Big thoughts.
                <br />
                <span className="text-primary">Clear next steps.</span>
              </h1>
              <p className="chat-welcome-description text-muted-foreground">
                A thinking partner for the first draft, the tricky question, and
                whatever comes next.
              </p>
              <Suggestions disabled={isBusy} onSelect={sendMessage} />
            </ConversationEmptyState>
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isStreaming={isBusy && message.id === lastMessage?.id}
              />
            ))
          )}
          {status === "submitted" && (
            <div className="flex items-center gap-2 text-sm" role="status">
              <span
                aria-hidden="true"
                className="flex size-7 items-center justify-center rounded-lg bg-primary font-serif text-primary-foreground"
              >
                h.
              </span>
              <Shimmer as="span">Harvey is thinking…</Shimmer>
            </div>
          )}
        </ConversationContent>
        {messages.length > 0 && (
          <ConversationDownload
            messages={messages.map(toUIMessage)}
            formatMessage={formatForDownload}
            filename="harvey-conversation.md"
            aria-label="Download conversation"
            disabled={isBusy}
          />
        )}
        <ConversationScrollButton aria-label="Scroll to latest message" />
      </Conversation>

      <div className="mx-auto flex w-full max-w-3xl shrink-0 flex-col gap-3 px-5 pt-3 pb-4 sm:px-8 sm:pb-6">
        {error && (
          <Alert variant="destructive">
            <AlertTitle className="flex items-center justify-between gap-2">
              Couldn’t finish this response
              <Button
                variant="ghost"
                size="icon-xs"
                aria-label="Dismiss error"
                onClick={clearError}
              >
                <XIcon />
              </Button>
            </AlertTitle>
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
        )}
        <PromptForm status={status} onSubmit={sendMessage} onStop={stop} />
        <p className="text-center text-[11px] text-muted-foreground">
          Harvey can make mistakes. Check important details.
        </p>
      </div>
    </main>
  )
}
