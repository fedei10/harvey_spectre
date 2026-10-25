import type { Metadata } from "next"

import { Chat } from "@/components/chat"

export const metadata: Metadata = {
  title: "Harvey — Space to think",
  description: "A streaming Groq assistant with conversation memory.",
}

export default function Page() {
  return <Chat />
}
