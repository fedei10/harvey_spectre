"use client"

import * as React from "react"
import { CheckIcon, ChevronDownIcon } from "lucide-react"

import {
  ModelSelector,
  ModelSelectorContent,
  ModelSelectorGroup,
  ModelSelectorItem,
  ModelSelectorList,
  ModelSelectorName,
  ModelSelectorTrigger,
} from "@/components/ai-elements/model-selector"
import {
  PromptInput,
  PromptInputBody,
  PromptInputButton,
  PromptInputFooter,
  PromptInputProvider,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
  usePromptInputController,
} from "@/components/ai-elements/prompt-input"

// ponytail: display-only — the backend picks the model via GROQ_MODEL_NAME.
// Make this a real choice when the backend accepts a model per request.
const MODEL = { id: "openai/gpt-oss-120b", name: "GPT OSS 120B · Groq" }

type Status = "ready" | "submitted" | "streaming"

export function PromptForm({
  status,
  onSubmit,
  onStop,
}: {
  status: Status
  onSubmit: (text: string) => void
  onStop: () => void
}) {
  return (
    <PromptInputProvider>
      <PromptInput
        className="prompt-surface"
        aria-label="Chat message"
        onSubmit={({ text }) => {
          // Throwing keeps the draft in the textarea instead of clearing it.
          if (status !== "ready" || !text.trim())
            throw new Error("Not ready to send")
          onSubmit(text.trim())
        }}
      >
        <PromptInputBody>
          <PromptInputTextarea
            placeholder="Ask Harvey anything…"
            aria-label="Message Harvey"
            className="max-h-48 min-h-20 px-5 pt-4"
          />
        </PromptInputBody>
        <PromptInputFooter className="px-3 pb-3">
          <PromptInputTools>
            <ModelPicker />
            <span className="hidden text-[11px] text-muted-foreground sm:inline">
              Shift + Enter for a new line
            </span>
          </PromptInputTools>
          <SubmitButton status={status} onStop={onStop} />
        </PromptInputFooter>
      </PromptInput>
    </PromptInputProvider>
  )
}

function SubmitButton({
  status,
  onStop,
}: {
  status: Status
  onStop: () => void
}) {
  const { textInput } = usePromptInputController()
  return (
    <PromptInputSubmit
      status={status}
      onStop={onStop}
      aria-label={status === "ready" ? "Send message" : "Stop generating"}
      disabled={status === "ready" && !textInput.value.trim()}
    />
  )
}

function ModelPicker() {
  const [open, setOpen] = React.useState(false)
  return (
    <ModelSelector open={open} onOpenChange={setOpen}>
      <ModelSelectorTrigger
        render={<PromptInputButton size="sm" className="gap-1.5" />}
      >
        <span aria-hidden="true" className="font-serif text-base text-primary">
          h.
        </span>
        <span className="text-xs">{MODEL.name}</span>
        <ChevronDownIcon className="size-3.5 text-muted-foreground" />
      </ModelSelectorTrigger>
      <ModelSelectorContent title="Choose a model">
        <ModelSelectorList>
          <ModelSelectorGroup heading="Groq">
            <ModelSelectorItem value={MODEL.id} onSelect={() => setOpen(false)}>
              <ModelSelectorName>{MODEL.name}</ModelSelectorName>
              <CheckIcon className="ml-auto size-4" />
            </ModelSelectorItem>
          </ModelSelectorGroup>
        </ModelSelectorList>
      </ModelSelectorContent>
    </ModelSelector>
  )
}
