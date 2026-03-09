from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


RAW_CONVO_DIR = PROJECT_ROOT / "data" / "raw_conversations"
PROCESSED_MEMORY_DIR = PROJECT_ROOT / "data" / "processed_memory"

RAW_CONVO_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
# LLM CONFIGURATION
LLM_PROVIDER = "ollama"

OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_M"