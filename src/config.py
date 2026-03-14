from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_CONVO_DIR = DATA_DIR / "raw_conversations"

# Projects folder
PROJECTS_DIR = DATA_DIR / "projects"

# Current project name
PROJECT_NAME = "ai_context_memory_system"

# Project directory
PROJECT_DIR = PROJECTS_DIR / PROJECT_NAME

# Memory packets location
PROCESSED_MEMORY_DIR = PROJECT_DIR

# Vector index location
VECTOR_INDEX_DIR = PROJECT_DIR / "vector_index"

# Ensure folders exist
RAW_CONVO_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)
# LLM CONFIGURATION
LLM_PROVIDER = "ollama"

OLLAMA_BASE_URL = "http://localhost:11434"

# Models
CONTEXT_MODEL = "qwen2.5:7b-instruct-q4_K_M"
DEV_MODEL = "qwen2.5-coder:7b"

CONTEXT_MODEL_FALLBACKS = [
    "qwen2.5:3b-instruct",
    "llama3.2:3b-instruct",
    "phi3:mini",
    "gemma2:2b",
    "qwen2.5:1.5b-instruct",
]
