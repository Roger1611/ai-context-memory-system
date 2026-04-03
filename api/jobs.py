import uuid
from datetime import datetime, timezone
from typing import Optional

_jobs: dict[str, dict] = {}


def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return job_id


def update_job(job_id: str, status: str, result: Optional[str] = None, error: Optional[str] = None) -> None:
    job = _jobs.get(job_id)
    if job is None:
        return
    job["status"] = status
    if result is not None:
        job["result"] = result
    if error is not None:
        job["error"] = error


def get_job(job_id: str) -> Optional[dict]:
    return _jobs.get(job_id)
