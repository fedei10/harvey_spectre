// Display label for the model configured by backend GROQ_MODEL_NAME.
export const MODELS = [
  { id: "openai/gpt-oss-120b", name: "GPT OSS 120B · Groq" },
]

export const DEFAULT_MODEL = MODELS[0].id

export interface GatewayModel {
  id: string
  name: string
}

export function isModelAllowed(id: string) {
  return MODELS.some((model) => model.id === id)
}
