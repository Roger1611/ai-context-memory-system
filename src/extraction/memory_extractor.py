import json
from pathlib import Path

from src.llm.ollama_client import OllamaError, generate_response, list_local_models
from src.extraction.extraction_prompt import (
    build_chunk_summary_prompt,
    build_extraction_prompt,
)
from src.extraction.schema import create_memory_packet
from src.config import CONTEXT_MODEL, CONTEXT_MODEL_FALLBACKS, PROCESSED_MEMORY_DIR
from src.utils.conversation_chunker import chunk_text

_LOCAL_MODEL_NAMES = None
_WORKING_CONTEXT_MODEL = None

def _model_variants(name):
    variants = {name}
    if "-q4_" in name:
        variants.add(name.split("-q4_", 1)[0])
    if ":" in name:
        base, tag = name.split(":", 1)
        variants.add(f"{base}:{tag.split('-q', 1)[0]}")
    return {variant for variant in variants if variant}


def _get_local_model_names():
    global _LOCAL_MODEL_NAMES

    if _LOCAL_MODEL_NAMES is not None:
        return _LOCAL_MODEL_NAMES

    local_models = list_local_models()
    _LOCAL_MODEL_NAMES = [model.get("name", "") for model in local_models if model.get("name")]
    return _LOCAL_MODEL_NAMES


def _candidate_context_models():
    global _WORKING_CONTEXT_MODEL

    try:
        local_names = _get_local_model_names()
    except OllamaError:
        fallback_names = [CONTEXT_MODEL, *CONTEXT_MODEL_FALLBACKS]
        if _WORKING_CONTEXT_MODEL:
            return _dedupe_models([_WORKING_CONTEXT_MODEL, *fallback_names])
        return _dedupe_models(fallback_names)

    configured_names = [CONTEXT_MODEL, *CONTEXT_MODEL_FALLBACKS]
    configured_variants = set()
    for name in configured_names:
        configured_variants.update(_model_variants(name))

    preferred = []

    if _WORKING_CONTEXT_MODEL:
        preferred.append(_WORKING_CONTEXT_MODEL)

    for name in configured_names:
        for local_name in local_names:
            if local_name == name or local_name in _model_variants(name) or name in _model_variants(local_name):
                preferred.append(local_name)

    instruct_like = [
        name
        for name in local_names
        if any(token in name.lower() for token in ("instruct", "chat", "mini", "3b", "2b", "1.5b"))
    ]
    family_matches = [
        name for name in local_names
        if any(variant.split(":", 1)[0] == name.split(":", 1)[0] for variant in configured_variants)
    ]

    return _dedupe_models([*preferred, *family_matches, *instruct_like, *local_names])


def _dedupe_models(models):
    seen = set()
    ordered = []
    for model in models:
        if not model or model in seen:
            continue
        seen.add(model)
        ordered.append(model)
    return ordered


def _generate_context_summary(prompt, prefer_small_models=False):
    global _WORKING_CONTEXT_MODEL

    errors = []
    models = _candidate_context_models()
    if prefer_small_models:
        small_models = [
            model
            for model in models
            if any(token in model.lower() for token in ("3b", "2b", "1.5b", "mini"))
        ]
        large_models = [model for model in models if model not in small_models]
        models = _dedupe_models([*small_models, *large_models])

    for model in models:
        try:
            if model != CONTEXT_MODEL:
                print(f"[WARN] Falling back to context model: {model}")
            response = generate_response(prompt, model, timeout=180).strip()
            _WORKING_CONTEXT_MODEL = model
            return response, model
        except OllamaError as exc:
            errors.append(f"{model}: {exc}")
            print(f"[WARN] Context model failed: {model} -> {exc}")
            lower_message = str(exc).lower()
            if any(
                token in lower_message
                for token in (
                    "actively refused",
                    "connection refused",
                    "failed to establish a new connection",
                    "max retries exceeded",
                )
            ):
                break
            continue

    joined_errors = "; ".join(errors) if errors else "No usable Ollama model was found."
    raise RuntimeError(f"Unable to generate context summary. {joined_errors}")


def _build_context_source_text(text):
    chunks = chunk_text(text, max_chars=12000)
    if len(chunks) <= 1:
        return text, None

    print(f"[INFO] Conversation is large. Summarizing {len(chunks)} chunks first...")
    chunk_summaries = []
    model_used = None

    for index, chunk in enumerate(chunks, start=1):
        prompt = build_chunk_summary_prompt(chunk, index, len(chunks))
        summary, model_used = _generate_context_summary(
            prompt,
            prefer_small_models=True,
        )
        chunk_summaries.append(
            f"Chunk {index} Summary:\n{summary}"
        )

    return "\n\n".join(chunk_summaries), model_used


def extract_memory_from_conversation(file_path: Path):
    print(f"\n[INFO] Extracting Context Summary from: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    convo_id = data.get("conversation_id", "unknown")
    text = "\n".join([m.get("content", "") for m in data.get("messages", [])])

    context_source_text, chunk_model_used = _build_context_source_text(text)
    prompt = build_extraction_prompt(context_source_text)
    print(f"[INFO] Generating fluid text summary with Context LLM...")
    response, model_used = _generate_context_summary(
        prompt,
        prefer_small_models=len(context_source_text) > 12000,
    )
    if chunk_model_used and model_used == CONTEXT_MODEL:
        print(f"[INFO] Chunk pre-summaries were generated with model: {chunk_model_used}")
    print(f"[INFO] Context summary generated with model: {model_used}")

    packet = create_memory_packet(
        "ai_context",
        "context_summary",
        "summary",
        response,
        convo_id,
        "context_extraction",
    )
    return [packet]


def save_memory_packets(packets):
    out = PROCESSED_MEMORY_DIR / "memory_packets.json"
    existing = json.load(open(out, "r", encoding="utf-8")) if out.exists() else []
    existing.extend(packets)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
