# Groq streaming chat frontend

Next.js chat UI built from the shadcn chatbot template. The browser sends messages to `/api/chat`; Next.js forwards them to FastAPI's `/v1/chat/stream` endpoint. FastAPI runs the Groq agent and streams AI SDK UI message events back to the browser.

## Run locally

Start the backend from `backend/`:

```bash
venv/bin/uvicorn app.main:app --reload --port 8000
```

In `frontend/`, install dependencies and configure the server URL:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. Keep `GROQ_API_KEY` and `GROQ_MODEL_NAME` in `backend/.env`. No AI Gateway key is needed. `BACKEND_URL` in `frontend/.env.local` defaults to `http://127.0.0.1:8000`; set it to the backend's reachable address when deploying.

## Chat behavior

- Replies render incrementally, including Markdown and multiline text.
- The UI chat ID is the backend conversation ID. SQLite keeps the conversation context.
- New Chat creates a new conversation; browser refresh does not restore the previous UI transcript.
- Stop aborts the stream. A stopped turn may leave partial context in the backend checkpoint.
- Groq and connection failures appear in the UI. Regeneration is not supported.
- The backend selects the model and runs its tools. The frontend model label in `lib/models.ts` should match `GROQ_MODEL_NAME`.
- Tool results are reflected in the assistant's reply; this integration does not render separate tool or reasoning events.

The old JSON `/v1/chat` endpoint remains available for compatibility. The frontend exclusively uses streaming.

## Checks

```bash
npm run typecheck
npm run lint
npm run build
```
