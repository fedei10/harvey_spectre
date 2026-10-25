# Harvey chat frontend

React renders messages from your FastAPI backend. There is no AI SDK, useChat,
AI Gateway, or frontend model provider. The UI uses shadcn chat primitives and
AI Elements-inspired conversation, message action, and prompt-input patterns.

## Run locally

Start the backend from `backend/`:

```bash
venv/bin/uvicorn app.main:app --reload --port 8000
```

In `frontend/`:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. Configure `GROQ_API_KEY` and `GROQ_MODEL_NAME` only in
`backend/.env`. Set `BACKEND_URL` in `frontend/.env.local` to your FastAPI address
(default: http://127.0.0.1:8000).

## Backend stream contract

The browser POSTs `{ "message": "Hello", "conversation_id": "uuid" }` to
`/api/chat`. This same-origin route only validates and forwards the request to
FastAPI `/v1/chat/stream`, then forwards its response bytes without buffering.
It does not run any models or tools.

FastAPI returns `text/event-stream` with JSON in each `data:` frame:

```text
data: {"type":"start","conversation_id":"uuid","message_id":"uuid"}

data: {"type":"delta","text":"Hello"}

data: {"type":"done"}

```

On failure, an `error` event with a safe `message` precedes `done`. The client
uses native fetch, AbortController, and TextDecoder. It preserves partial replies
on errors or stop, and reports truncated streams instead of treating them as success.

- PostgreSQL checkpoints retain conversation context across turns.
- New Chat creates a new conversation; reloading does not restore the UI transcript.
- Stop cancels the request; a stopped turn may leave partial backend context.
- Download exports the visible conversation as Markdown.
- The backend selects the model and executes tools. Tool results appear in the
  final reply; there are no separate tool or reasoning events in this protocol.
- `/v1/chat` remains available for non-streaming JSON clients.

## Checks

```bash
npm test
npm run typecheck
npm run lint
npm run build
```
