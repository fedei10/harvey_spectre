"use client"

import * as React from "react"
import {
  CheckIcon,
  CircleStopIcon,
  CopyIcon,
  TriangleAlertIcon,
} from "lucide-react"

import {
  Message,
  MessageAction,
  MessageActions,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message"
import { Shimmer } from "@/components/ai-elements/shimmer"
import { type ChatMessage as BackendMessage } from "@/lib/chat-stream"

export function ChatMessage({
  message,
  isStreaming = false,
}: {
  message: BackendMessage
  isStreaming?: boolean
}) {
  if (message.role === "user")
    return (
      <Message from="user">
        <MessageContent className="whitespace-pre-wrap">
          {message.text}
        </MessageContent>
      </Message>
    )
  return (
    <Message from="assistant" className="max-w-full">
      <div className="flex items-center gap-2 text-sm font-medium">
        <span
          aria-hidden="true"
          className="flex size-7 items-center justify-center rounded-lg bg-primary font-serif text-primary-foreground"
        >
          h.
        </span>
        Harvey
        <span className="ml-auto flex items-center gap-1 text-xs font-normal text-muted-foreground">
          {isStreaming ? (
            <Shimmer as="span" duration={1.5}>
              Writing…
            </Shimmer>
          ) : message.state === "stopped" ? (
            <>
              <CircleStopIcon className="size-3" />
              Stopped
            </>
          ) : message.state === "error" ? (
            <>
              <TriangleAlertIcon className="size-3" />
              Incomplete
            </>
          ) : null}
        </span>
      </div>
      <MessageContent className="w-full text-[15px] leading-7">
        <MessageResponse isAnimating={isStreaming}>{message.text}</MessageResponse>
      </MessageContent>
      {!isStreaming && message.text && <CopyAction text={message.text} />}
    </Message>
  )
}

function CopyAction({ text }: { text: string }) {
  const [copied, setCopied] = React.useState(false)

  React.useEffect(() => {
    if (!copied) return
    const timeout = setTimeout(() => setCopied(false), 2000)
    return () => clearTimeout(timeout)
  }, [copied])

  return (
    <MessageActions>
      <MessageAction
        tooltip={copied ? "Copied" : "Copy"}
        onClick={() => {
          navigator.clipboard
            .writeText(text)
            .then(() => setCopied(true))
            .catch(() => {})
        }}
      >
        {copied ? <CheckIcon /> : <CopyIcon />}
      </MessageAction>
    </MessageActions>
  )
}
