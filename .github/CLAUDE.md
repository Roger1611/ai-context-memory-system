# CLAUDE.md — AI Context Memory System

## Update Log

### 2026-04-03
- Switched LLM provider from Ollama to **OpenRouter** (`deepseek/deepseek-v3.2`)
- Added `src/ingestion/fetch_share_link_http.py` — `requests`-based fetcher, now active in all entry points
- `fetch_share_link.py` (Playwright) preserved on disk but not wired in; swap comment in `memory_sync.py:14` and `scripts/run_ingestion.py:1` to reactivate
- Created `api/main.py` and `api/jobs.py` — FastAPI backend with job queue (`POST /extract`, `GET /status/{job_id}`)
- Created `frontend/` — Vite + React + Tailwind SPA with idle / loading / done / error states
- Added `requirements-api.txt` and `render.yaml` for Render deployment
- Rewrote `_build_snapshot()` in `scripts/generate_project_snapshot.py` — clean format: header + raw content only, no separators or READY-TO-USE PROMPT section
- Fixed `_print_preview()` to use `sys.stdout.buffer` with `errors="replace"` — prevents cp1252 crash on Windows
- Added source conversation ID to snapshot header line for auditability
- Added strict grounding constraints to all three prompts in `src/extraction/extraction_prompt.py` — model must only report what is explicitly in the conversation; empty sections must be omitted or labelled "Nothing in this conversation."
- Added extraction validation in `api/main.py` — raises error if extracted word count exceeds source conversation word count

---

## Project Overview

A lightweight memory layer that sits on top of AI tools. The system ingests AI chat share links, extracts durable project knowledge using a local LLM, stores it as structured JSON memory packets, indexes them with FAISS embeddings, and generates project snapshots that can be pasted into future AI sessions to restore context instantly.

**Business goal:** Sell this as a productivity tool for developers and researchers who work on long-running AI-assisted projects.

---

## Actual Project Structure

```
ai-context-memory-system/
├── memory_sync.py                          # Main pipeline entrypoint — run this
├── requirements.txt
├── requirements-api.txt                    # Dependencies for the FastAPI backend only
├── render.yaml                             # Render deployment config for the API
│
├── api/                                    # FastAPI backend
│   ├── main.py                             # Three endpoints: GET /, POST /extract, GET /status/{job_id}
│   └── jobs.py                             # In-memory job store (create/update/get)
│
├── frontend/                               # Vite + React + Tailwind SPA
│   ├── src/
│   │   ├── App.jsx                         # Single-page app: idle / loading / done / error states
│   │   └── index.css                       # Tailwind base + component classes
│   ├── .env.local                          # VITE_API_URL=http://localhost:8000 (local dev)
│   ├── vercel.json                         # Vercel static deployment config
│   └── tailwind.config.js
│
├── data/
│   ├── raw_conversations/
│   │   └── sessions/                       # Each run creates a session_XXXXXX/ subfolder
│   │       └── <session_id>/
│   │           └── <convo_id>.json         # Raw ingested conversation JSON
│   └── projects/
│       └── ai_context_memory_system/       # All outputs land here (config.PROJECT_DIR)
│           ├── memory_packets.json         # All extracted packets combined
│           ├── context_snapshot.txt        # Human-readable context summary
│           ├── developer_snapshot.txt      # Developer-readable repo/code summary
│           └── vector_index/
│               ├── faiss_index.bin
│               └── metadata.json
│
├── scripts/
│   ├── build_index.py                      # Builds FAISS index from memory_packets.json
│   ├── generate_project_snapshot.py        # Writes context_snapshot.txt
│   ├── generate_dev_snapshot.py            # Writes developer_snapshot.txt
│   ├── generate_full_context.py            # Prints all packets grouped by topic
│   ├── run_ingestion.py                    # Standalone ingestion without extraction
│   ├── run_extraction.py                   # Standalone extraction over raw convos
│   ├── test_llm.py                         # Smoke test for OpenRouter connection
│   ├── test_http_fetch.py                  # CLI test for fetch_share_link_http
│   ├── test_retrieval.py                   # Interactive FAISS search test
│   └── test_prompt_generation.py          # Interactive prompt builder test
│
└── src/
    ├── config.py                           # All paths + LLM model config
    ├── llm/
    │   ├── __init__.py                     # Re-exports generate_response
    │   └── openrouter_client.py            # HTTP client for OpenRouter API
    ├── ingestion/
    │   ├── __init__.py
    │   ├── fetch_share_link.py             # Playwright headless fetch (kept, not active)
    │   ├── fetch_share_link_http.py        # requests-based fetch — currently active
    │   └── conversation_parser.py          # BeautifulSoup HTML → messages list
    ├── extraction/
    │   ├── __init__.py
    │   ├── schema.py                       # create_memory_packet() factory
    │   ├── artifact_extractor.py           # Regex-based: trees, paths, imports, commands
    │   ├── extraction_prompt.py            # Prompts for context LLM summarization
    │   ├── memory_extractor.py             # Orchestrates LLM extraction + chunking
    │   ├── dev_extraction_prompt.py        # Prompt for developer handoff LLM
    │   └── dev_memory_extractor.py         # LLM-based dev knowledge extraction
    ├── retrieval/
    │   ├── __init__.py
    │   ├── embedding_model.py              # SentenceTransformer (all-MiniLM-L6-v2)
    │   ├── vector_index.py                 # FAISS IndexFlatL2 wrapper (save/load/search)
    │   └── memory_search.py               # Loads index, runs semantic search
    ├── prompt_generation/
    │   ├── __init__.py
    │   └── prompt_builder.py              # Builds RAG-style prompt from search results
    └── utils/
        ├── __init__.py
        ├── conversation_chunker.py         # Splits long text into ~12k char chunks
        ├── id_generator.py                # Generates conv_XXXXXXXX IDs
        └── packet_deduplicator.py         # Dedupes packets by (topic, type, content)
```

---

## Pipeline Flow (memory_sync.py)

```
User input: share links + platform
        ↓
fetch_share_link_http.py  → requests fetches static HTML (active)
fetch_share_link.py       → Playwright version kept for JS-rendered pages (swap comment in memory_sync.py:14)
        ↓
conversation_parser.py   → BeautifulSoup extracts messages list
        ↓
Saved to data/raw_conversations/sessions/<session_id>/<convo_id>.json
        ↓
extract_memory_from_conversation()  → memory_extractor.py (LLM via OpenRouter)
        ↓                  chunks if >24k chars, summarizes each chunk,
        ↓                  then generates final context summary packet
All packets merged → remove_duplicate_packets() → save to memory_packets.json
        ↓
build_index.py           → embed all packet contents → FAISS index
        ↓
generate_project_snapshot.py  → context_snapshot.txt  (context_extraction packets)
```

## API Flow (api/main.py)

```
POST /extract {url}
        ↓
fetch_share_link_http.fetch_share_page(url)
        ↓
parse_conversation(html, source="chatgpt")
        ↓
Save raw convo JSON to data/raw_conversations/sessions/api_<job_id>/
        ↓
extract_memory_from_conversation(file_path) → packets
        ↓
_build_snapshot(ctx_packets) → snapshot string
        ↓
job.result = snapshot  →  GET /status/{job_id} returns it
```

---

## Memory Packet Schema

Defined in `src/extraction/schema.py`. Every packet is a flat dict:

```json
{
  "project": "ai_context",
  "topic": "string — file path, 'folder_structure', 'command', 'context_summary', etc.",
  "type": "folder_structure | file_role | module_import | command | entrypoint | code_block | summary | dev_summary",
  "content": "string — the actual extracted content",
  "source_conversation": "8-char conversation UUID",
  "source": "dev_extraction | context_extraction"
}
```

The `source` field determines which snapshot a packet appears in:
- `dev_extraction` → `developer_snapshot.txt`
- `context_extraction` → `context_snapshot.txt`

---

## Configuration (src/config.py)

All paths and model names are centralized here. **Never hardcode paths anywhere else.**

```python
PROJECT_ROOT         # repo root
DATA_DIR             # data/
RAW_CONVO_DIR        # data/raw_conversations/
PROJECTS_DIR         # data/projects/
PROJECT_NAME         # "ai_context_memory_system"
PROJECT_DIR          # data/projects/ai_context_memory_system/
PROCESSED_MEMORY_DIR # same as PROJECT_DIR — memory_packets.json lives here
VECTOR_INDEX_DIR     # data/projects/ai_context_memory_system/vector_index/

OPENROUTER_API_KEY   # from .env
OPENROUTER_MODEL     # from .env — currently "deepseek/deepseek-v3.2"
```

To swap the model, update `OPENROUTER_MODEL` in `.env`. The fallback default in `config.py` is also `deepseek/deepseek-v3.2`.

---

## LLM Setup

The system uses **OpenRouter** for LLM inference. Set credentials in `.env`:

```
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=deepseek/deepseek-v3.2
```

The client is `src/llm/openrouter_client.py`. It reads model from env at call time, so changing `.env` takes effect on next server restart.

---

## Fetcher: HTTP vs Playwright

Two fetchers exist side by side:

| File | Method | Active |
|---|---|---|
| `src/ingestion/fetch_share_link_http.py` | `requests` — fast, no browser | Yes |
| `src/ingestion/fetch_share_link.py` | Playwright — required for JS-rendered pages | No |

To swap back to Playwright, change the commented import in `memory_sync.py:14` and `scripts/run_ingestion.py:1`:
```python
# swap this:
from src.ingestion.fetch_share_link_http import fetch_share_page
# back to:
from src.ingestion.fetch_share_link import fetch_share_page
```

**Known limitation:** ChatGPT share pages are JS-rendered. The HTTP fetcher gets the static shell only — conversation content may be thin or missing. Playwright fetcher resolves this but requires `playwright install chromium`.

---

## Snapshot Format

`_build_snapshot()` in `scripts/generate_project_snapshot.py` outputs:

```
Project Context - generated {date}

{raw content from context_extraction packets}
```

No separators, no metadata block, no model name, no READY-TO-USE PROMPT section. Plain ASCII only — no Unicode box-drawing characters.

---

## Running the Project

```bash
# Install pipeline dependencies
pip install -r requirements.txt

# Run full pipeline
python memory_sync.py
# → prompts for share links (one per line, blank line to finish)
# → prompts for platform: chatgpt / claude / gemini

# Test HTTP fetcher
python scripts/test_http_fetch.py <url>

# Run individual scripts
python scripts/test_llm.py                # check OpenRouter is working
python scripts/test_retrieval.py          # interactive semantic search
python scripts/build_index.py             # rebuild FAISS index from existing packets
```

## Running the API + Frontend

```bash
# Terminal 1 — backend
pip install -r requirements-api.txt
uvicorn api.main:app --port 8000 --reload

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
# → open http://localhost:5173
```

---

## Two Extraction Paths

### 1. Context Extraction (LLM-based)
`src/extraction/memory_extractor.py` — sends conversation to OpenRouter:
- Chunks conversations longer than 24k chars via `conversation_chunker.py`
- Summarizes each chunk separately if needed
- Combines chunk summaries and generates a final context packet
- Output is a single `summary` packet with Markdown content (5 sections)

### 2. Dev Extraction (regex-based, no LLM, fast)
`src/extraction/artifact_extractor.py` — pure regex over raw conversation text:
- `extract_folder_trees()` — detects ASCII tree structures (├, └, │)
- `extract_file_paths()` — finds `.py` file references
- `extract_module_imports()` — finds `import` and `from x import` statements
- `extract_commands()` — finds lines starting with `python`, `pip`, `git`, etc.
- `extract_entrypoints()` — infers main scripts from commands + filename patterns
- `extract_code_blocks()` — extracts triple-backtick code blocks with filenames

---

## Key Design Decisions

- **OpenRouter for LLM**: switched from local Ollama to OpenRouter. Model is `deepseek/deepseek-v3.2` by default, configurable via `.env`.
- **HTTP fetcher active**: `fetch_share_link_http.py` is the default. Playwright version preserved but not wired in. See limitation note above.
- **Flat JSON storage**: `memory_packets.json` is a single JSON array. The FAISS index is always rebuildable — never treat it as source of truth.
- **Packets are append-only**: never mutate existing packets. Add a `supersedes` field if correcting old data.
- **All file paths go through `src/config.py`**: no hardcoded paths anywhere else.
- **API does not write memory_packets.json**: the API pipeline creates packets in memory, builds a snapshot, and discards them. Only `memory_sync.py` persists packets to disk.

---

## Development Rules

1. **Never hardcode paths** — always import from `src.config`.
2. **Never mutate existing packets** — append only.
3. **Ingestion modules must stay stateless** — fetchers and parsers return data only. All file writes happen in `memory_sync.py` or `api/main.py`.
4. **Extraction failures must log, not silently fail** — surface errors visibly; never swallow exceptions in the extraction pipeline.
5. **The extraction prompt is source code** — changes to `extraction_prompt.py` must be tested against example conversations before committing.
6. **Platform parsers are isolated** — adding Claude or Gemini parsing means modifying only `conversation_parser.py`.
7. **No Unicode box-drawing characters in snapshot output** — use plain ASCII `-` and `=` only. Windows cp1252 terminals will corrupt U+2500 and similar characters.

---

## Current Status

- [x] Ingestion: ChatGPT share link fetch (HTTP via requests)
- [x] Ingestion: ChatGPT share link fetch (Playwright — preserved, not active)
- [x] Conversation parsing (BeautifulSoup, role-tagged messages)
- [x] Context extraction: OpenRouter LLM chain with chunking
- [x] Memory packet schema and deduplication
- [x] FAISS index builder + semantic search
- [x] Context snapshot generator (clean format: header + content only)
- [x] Developer snapshot generator
- [x] Full pipeline orchestrator (memory_sync.py)
- [x] FastAPI backend (api/main.py) with job queue
- [x] React + Vite + Tailwind frontend (frontend/)
- [ ] Ingestion: Claude share link parsing
- [ ] Ingestion: Gemini share link parsing
- [ ] Per-project isolation (PROJECT_NAME is currently hardcoded in config.py)
- [ ] Fix JS-rendering gap: ChatGPT share pages need Playwright to get full conversation content

## Current TASK
To build a prototype to give to all kinds of users to get feedback.
