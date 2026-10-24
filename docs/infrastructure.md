# PostgreSQL and Redis integration

This step adds infrastructure connections only. LangGraph still uses the existing
SQLite checkpointer until it is migrated in a separate change.

## Setup

From the repository root, create a local environment file and set a strong password:

```bash
cp backend/.env.example backend/.env
# Edit POSTGRES_PASSWORD in backend/.env
docker compose --env-file backend/.env up -d postgres redis
docker compose --env-file backend/.env ps
```

Run FastAPI locally:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
curl -i http://127.0.0.1:8000/test
```

Expected status 200:

```json
{"postgres":"connected","redis":"connected"}
```

Alternatively, run FastAPI in Docker from the repository root:

```bash
docker compose --env-file backend/.env --profile api up --build -d
```

The optional API container uses internal Docker hostnames for PostgreSQL and
Redis. Persistent Docker volumes store PostgreSQL data, Redis data, and the
current SQLite checkpoint file. The `/test` route returns 503 if either
connection is unavailable and does not call the Groq API. Use the existing
`/v1/health/GROQ` probe for Groq.

**Warning:** `docker compose down -v` deletes persistent volumes. Local
loopback port bindings are development-only; production requires secrets,
private networking, backups, and authenticated Redis.
