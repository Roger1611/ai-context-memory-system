import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")

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
