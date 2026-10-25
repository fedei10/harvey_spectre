"use client"

import Link from "next/link"
import { MoonIcon, SunIcon } from "lucide-react"
import { useTheme } from "next-themes"
import { NewChatButton } from "@/components/new-chat-button"
import { Button } from "@/components/ui/button"

export function SiteHeader() {
  const { resolvedTheme, setTheme } = useTheme()
  return (
    <header className="flex shrink-0 items-center justify-between gap-4 border-b border-border/60 px-5 py-4 sm:px-10">
      <Link
        href="/"
        aria-label="Harvey home"
        className="flex items-center gap-3"
      >
        <span
          aria-hidden="true"
          className="flex size-9 items-center justify-center rounded-xl bg-primary font-serif text-xl text-primary-foreground"
        >
          h.
        </span>
        <span className="flex flex-col">
          <span className="text-sm font-semibold tracking-[0.18em]">
            HARVEY
          </span>
          <span className="hidden text-[11px] text-muted-foreground sm:inline">
            A little clarity goes a long way.
          </span>
        </span>
      </Link>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle color theme"
          onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
        >
          <SunIcon className="hidden dark:block" />
          <MoonIcon className="dark:hidden" />
        </Button>
        <NewChatButton />
      </div>
    </header>
  )
}
