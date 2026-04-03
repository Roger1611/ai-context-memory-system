import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.jobs import create_job, get_job, update_job
from src.config import RAW_CONVO_DIR
from src.extraction.memory_extractor import extract_memory_from_conversation
from src.ingestion.conversation_parser import parse_conversation
from src.ingestion.fetch_share_link_http import fetch_share_page
from scripts.generate_project_snapshot import _build_snapshot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_DIR = RAW_CONVO_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


class ExtractRequest(BaseModel):
    url: str


def _run_pipeline(job_id: str, url: str) -> None:
    try:
        update_job(job_id, "processing")

        # Fetch
        html = fetch_share_page(url)

        # Parse
        messages = parse_conversation(html, source="chatgpt")

        # Save raw conversation to disk
        convo_id = str(uuid.uuid4())[:8]
        session_path = SESSION_DIR / f"api_{job_id[:6]}"
        session_path.mkdir(exist_ok=True)
        file_path = session_path / f"{convo_id}.json"

        convo = {
            "conversation_id": convo_id,
            "session_id": f"api_{job_id[:6]}",
            "source": "chatgpt",
            "share_link": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "messages": messages,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(convo, f, indent=2)

        # Extract memory packets
        packets = extract_memory_from_conversation(file_path)

        # Build snapshot string from packets (no disk write needed)
        ctx_packets = [p for p in packets if p.get("source") == "context_extraction"]
        if not ctx_packets:
            raise RuntimeError("Extraction produced no context_extraction packets.")

        snapshot = _build_snapshot(ctx_packets)

        update_job(job_id, "done", result=snapshot)

    except Exception as e:
        update_job(job_id, "error", error=str(e))


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/extract")
def extract(request: ExtractRequest):
    if not request.url.strip():
        raise HTTPException(status_code=422, detail="url must be a non-empty string")

    job_id = create_job()
    thread = threading.Thread(target=_run_pipeline, args=(job_id, request.url), daemon=True)
    thread.start()

    return {"job_id": job_id}


@app.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
