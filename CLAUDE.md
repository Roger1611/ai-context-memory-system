# CLAUDE.md — AI Context Memory System

## Project Overview

A lightweight memory layer that sits on top of AI tools. The system ingests AI chat share links, extracts durable project knowledge using a local LLM, stores it as structured JSON memory packets, indexes them with FAISS embeddings, and generates project snapshots that can be pasted into future AI sessions to restore context instantly.

**Business goal:** Sell this as a productivity tool for developers and researchers who work on long-running AI-assisted projects.

---

## Actual Project Structure

```
ai-context-memory-system/
├── memory_sync.py                          # Main pipeline entrypoint — run this
├── requirements.txt
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
│   ├── test_llm.py                         # Smoke test for Ollama connection
│   ├── test_retrieval.py                   # Interactive FAISS search test
│   └── test_prompt_generation.py          # Interactive prompt builder test
│
└── src/
    ├── config.py                           # All paths + LLM model config
    ├── llm/
    │   ├── __init__.py                     # Re-exports generate_response
    │   └── ollama_client.py               # HTTP client for Ollama /api/generate
    ├── ingestion/
    │   ├── __init__.py
    │   ├── fetch_share_link.py            # Playwright headless fetch → raw HTML
    │   └── conversation_parser.py         # BeautifulSoup HTML → messages list
    ├── extraction/
    │   ├── __init__.py
    │   ├── schema.py                      # create_memory_packet() factory
    │   ├── artifact_extractor.py          # Regex-based: trees, paths, imports, commands
    │   ├── extraction_prompt.py           # Prompts for context LLM summarization
    │   ├── memory_extractor.py            # Orchestrates LLM extraction + chunking
    │   ├── dev_extraction_prompt.py       # Prompt for developer handoff LLM
    │   └── dev_memory_extractor.py        # LLM-based dev knowledge extraction
    ├── retrieval/
    │   ├── __init__.py
    │   ├── embedding_model.py             # SentenceTransformer (all-MiniLM-L6-v2)
    │   ├── vector_index.py                # FAISS IndexFlatL2 wrapper (save/load/search)
    │   └── memory_search.py              # Loads index, runs semantic search
    ├── prompt_generation/
    │   ├── __init__.py
    │   └── prompt_builder.py             # Builds RAG-style prompt from search results
    └── utils/
        ├── __init__.py
        ├── conversation_chunker.py        # Splits long text into ~12k char chunks
        ├── id_generator.py               # Generates conv_XXXXXXXX IDs
        └── packet_deduplicator.py        # Dedupes packets by (topic, type, content)
```

---

## Pipeline Flow (memory_sync.py)

```
User input: share links + platform
        ↓
fetch_share_link.py      → Playwright fetches HTML
        ↓
conversation_parser.py   → BeautifulSoup extracts messages list
        ↓
Saved to data/raw_conversations/sessions/<session_id>/<convo_id>.json
        ↓
build_dev_packets()      → artifact_extractor.py (pure regex, no LLM)
        ↓                  extracts: folder trees, file paths, module imports,
        ↓                  commands, entrypoints, code blocks
extract_memory_from_conversation()  → memory_extractor.py (LLM)
        ↓                  chunks if >12k chars, summarizes each chunk,
        ↓                  then generates final context summary packet
All packets merged → remove_duplicate_packets() → save to memory_packets.json
        ↓
build_index.py           → embed all packet contents → FAISS index
        ↓
generate_project_snapshot.py  → context_snapshot.txt  (context_extraction packets)
generate_dev_snapshot.py      → developer_snapshot.txt (dev_extraction packets)
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

LLM_PROVIDER         # "ollama"
OLLAMA_BASE_URL      # "http://localhost:11434"
CONTEXT_MODEL        # "qwen2.5:7b-instruct-q4_K_M"  (primary)
DEV_MODEL            # "qwen2.5-coder:7b"
CONTEXT_MODEL_FALLBACKS  # list of fallback model names tried in order
```

---

## LLM Setup

The system uses **Ollama** running locally. No external API keys required.

```bash
# Install Ollama: https://ollama.com
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull qwen2.5-coder:7b

# Verify Ollama is running before running the pipeline
curl http://localhost:11434/api/tags
```

`memory_extractor.py` has automatic model fallback logic — it queries `GET /api/tags` to discover locally available models and tries them in priority order if the primary model fails.

---

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run full pipeline
python memory_sync.py
# → prompts for share links (one per line, blank line to finish)
# → prompts for platform: chatgpt / claude / gemini

# Run individual scripts
python scripts/test_llm.py                # check Ollama is working
python scripts/test_retrieval.py          # interactive semantic search
python scripts/test_prompt_generation.py  # test RAG prompt builder
python scripts/build_index.py             # rebuild FAISS index from existing packets
```

---

## Two Extraction Paths

### 1. Dev Extraction (regex-based, no LLM, fast)
`src/extraction/artifact_extractor.py` — pure regex over raw conversation text:
- `extract_folder_trees()` — detects ASCII tree structures (├, └, │)
- `extract_file_paths()` — finds `.py` file references
- `extract_module_imports()` — finds `import` and `from x import` statements
- `extract_commands()` — finds lines starting with `python`, `pip`, `git`, etc.
- `extract_entrypoints()` — infers main scripts from commands + filename patterns
- `extract_code_blocks()` — extracts triple-backtick code blocks with filenames

### 2. Context Extraction (LLM-based, slower)
`src/extraction/memory_extractor.py` — sends conversation to Ollama:
- Chunks conversations longer than 12k chars via `conversation_chunker.py`
- Summarizes each chunk separately with a small model if needed
- Combines chunk summaries and generates a final context packet
- Output is a single `summary` packet with Markdown content

---

## Key Design Decisions

- **Local-first**: Ollama runs inference locally — private, no API costs.
- **Flat JSON storage**: `memory_packets.json` is a single JSON array. Simple to inspect and version-control. The FAISS index is always rebuildable from it — never treat the index as source of truth.
- **Two extraction modes**: Regex extraction (fast, deterministic) runs alongside LLM extraction (slow, semantic). Both write to the same packet file with different `source` values.
- **Packets are append-only**: `save_memory_packets()` always loads existing packets and extends them. To correct a bad packet, add a new one — do not mutate old ones.
- **All file paths go through `src/config.py`**: No hardcoded paths anywhere else in the codebase.
- **Model fallback is automatic**: If `CONTEXT_MODEL` is not available locally, `memory_extractor.py` queries Ollama for available models and tries fallbacks in order.

---

## Development Rules

1. **Never hardcode paths** — always import from `src.config`.
2. **Never mutate existing packets** — append only. Add a `supersedes` field if correcting old data.
3. **Ingestion modules must stay stateless** — `fetch_share_link.py` and `conversation_parser.py` return data only. All file writes happen in `memory_sync.py`.
4. **Extraction failures must log, not silently fail** — surface errors visibly; never swallow exceptions in the extraction pipeline.
5. **The extraction prompt is source code** — changes to `extraction_prompt.py` or `dev_extraction_prompt.py` must be tested against example conversations before committing.
6. **Platform parsers are isolated** — adding Claude or Gemini parsing means modifying only `conversation_parser.py`, not extraction or retrieval.

---

## Current Status

- [x] Ingestion: ChatGPT share link fetch (Playwright)
- [x] Conversation parsing (BeautifulSoup, role-tagged messages)
- [x] Dev extraction: folder trees, file paths, imports, commands, code blocks
- [x] Context extraction: Ollama LLM chain with chunking + fallback
- [x] Memory packet schema and deduplication
- [x] FAISS index builder + semantic search
- [x] Context snapshot generator
- [x] Developer snapshot generator
- [x] Full pipeline orchestrator (memory_sync.py)
- [ ] Ingestion: Claude share link parsing
- [ ] Ingestion: Gemini share link parsing
- [ ] Per-project isolation (PROJECT_NAME is currently hardcoded in config.py)
- [ ] UI for browsing stored memory packets

## Current TASK
To build a prototype to give to all kinds of users to get feedback.
