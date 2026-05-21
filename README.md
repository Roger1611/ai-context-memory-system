# ContextSync — AI Context Memory System

Stop re-explaining your project every time you start a new AI session.

ContextSync extracts durable knowledge from AI chat share links and turns it into a ready-to-paste context snapshot — so your next session picks up exactly where you left off.

---

## What It Does

Paste a ChatGPT share link. Get back a structured summary of everything worth carrying forward: decisions made, current state, open tasks, key details. Paste that into any new AI session and you're back up to speed!

The system works in two modes:

**Web app** — paste a link, get a snapshot in seconds via the hosted frontend  
**Local pipeline** — ingest multiple conversations, build a FAISS vector index, generate searchable project memory

---

## How It Works

1. A ChatGPT share link is submitted
2. The conversation is fetched via the [Apify ChatGPT extractor](https://apify.com/klinzinger/chatgpt-conversation-extractor) (handles JS-rendered pages)
3. An LLM (DeepSeek v3 via OpenRouter) extracts structured knowledge
4. The extracted content is returned as a context snapshot
5. Paste the snapshot into your next AI session

For the local pipeline, extracted packets are also stored as JSON, embedded with `all-MiniLM-L6-v2`, and indexed in FAISS for semantic search.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI (Python) |
| LLM | DeepSeek v3 via OpenRouter |
| Fetcher | Apify actor (JS-rendered page extraction) |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector search | FAISS |
| Frontend deploy | Vercel |
| API deploy | Render |

---

## Project Structure

```
contextsync/
├── memory_sync.py          # Local pipeline entrypoint
├── api/                    # FastAPI backend
│   ├── main.py             # POST /extract, GET /status/{job_id}
│   └── jobs.py             # In-memory job store
├── frontend/               # Vite + React + Tailwind SPA
│   └── src/App.jsx
├── src/
│   ├── config.py
│   ├── ingestion/          # Fetchers + conversation parser
│   ├── extraction/         # LLM prompts + memory extractor
│   ├── retrieval/          # FAISS index + semantic search
│   ├── prompt_generation/  # RAG prompt builder
│   └── utils/
└── scripts/                # Standalone build/test utilities
```

---

## Running Locally

### API + Frontend

```bash
# 1. Clone and install
git clone https://github.com/Roger1611/ai-context-memory-system
cd ai-context-memory-system

# 2. Set environment variables
cp .env.example .env
# Edit .env:
#   OPENROUTER_API_KEY=sk-or-...
#   OPENROUTER_MODEL=deepseek/deepseek-v3.2
#   APIFY_TOKEN=apify_api_...

# 3. Start the API
pip install -r requirements-api-lean.txt
uvicorn api.main:app --port 8000 --reload

# 4. Start the frontend (separate terminal)
cd frontend
npm install
npm run dev
# → open http://localhost:5173
```

### Local Pipeline (full memory system)

```bash
pip install -r requirements.txt
python memory_sync.py
# → prompts for share links and platform
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | Model string, e.g. `deepseek/deepseek-v3.2` |
| `APIFY_TOKEN` | Apify API token for conversation fetching |

---

## Deploying

**Frontend → Vercel**  
Connect the `frontend/` directory. Set `VITE_API_URL` to your Render API URL.

**API → Render**  
`render.yaml` is included. Set the three environment variables above in the Render dashboard.

---

## Memory Packet Format

The local pipeline stores extracted knowledge as flat JSON packets:

```json
{
  "project": "my_project",
  "topic": "context_summary",
  "type": "summary",
  "content": "...",
  "source_conversation": "a1b2c3d4",
  "source": "context_extraction"
}
```

---

## License

MIT