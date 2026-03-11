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

OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_M"
