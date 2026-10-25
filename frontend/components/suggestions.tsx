"use client"

import {
  CodeXmlIcon,
  LightbulbIcon,
  ListChecksIcon,
  PenLineIcon,
} from "lucide-react"

import {
  Suggestion,
  Suggestions as SuggestionRow,
} from "@/components/ai-elements/suggestion"

const suggestions = [
  {
    label: "Make something clear",
    icon: LightbulbIcon,
    prompt:
      "Explain how an API connects a frontend to a backend, using a simple example.",
  },
  {
    label: "Find the right words",
    icon: PenLineIcon,
    prompt:
      "Help me write a clear, thoughtful email. Ask me who it is for and what I want to say.",
  },
  {
    label: "Work through a problem",
    icon: CodeXmlIcon,
    prompt:
      "Help me debug my code. Ask me for the relevant code, the error, and what I expected to happen.",
  },
  {
    label: "Build a plan",
    icon: ListChecksIcon,
    prompt:
      "Help me turn a goal into a practical plan. Start by asking what I want to achieve and my deadline.",
  },
]

export function Suggestions({
  onSelect,
  disabled = false,
}: {
  onSelect: (prompt: string) => void
  disabled?: boolean
}) {
  return (
    <SuggestionRow className="w-full flex-wrap justify-center px-1 pb-1">
      {suggestions.map(({ label, icon: Icon, prompt }) => (
        <Suggestion
          key={label}
          suggestion={prompt}
          title={prompt}
          disabled={disabled}
          onClick={onSelect}
          className="starter-card gap-2"
        >
          <Icon className="text-primary" aria-hidden="true" />
          {label}
        </Suggestion>
      ))}
    </SuggestionRow>
  )
}
