"use client"

import { Button } from "@/components/ui/button"

const suggestions = [
  {
    label: "Tell me a story",
    prompt:
      "Tell me a short story. Format it in rich markdown: a title heading, a blockquote, a bulleted list, a table, and some bold and italic text.",
  },
  {
    label: "Explain an idea",
    prompt: "Explain how an API connects a frontend to a backend.",
  },
  {
    label: "Current UTC time",
    prompt: "Use get_current_time to tell me the current UTC time.",
  },
  {
    label: "Plan a dinner",
    prompt:
      "Help me plan a birthday dinner — ask me a few clarifying questions first, then suggest a menu.",
  },
]

export function Suggestions({
  onSelect,
}: {
  onSelect: (prompt: string) => void
}) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {suggestions.map((suggestion) => (
        <Button
          key={suggestion.label}
          variant="outline"
          size="sm"
          onClick={() => onSelect(suggestion.prompt)}
        >
          {suggestion.label}
        </Button>
      ))}
    </div>
  )
}
