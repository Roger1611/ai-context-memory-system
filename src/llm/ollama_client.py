import requests
import json
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

EXTRACTION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "enum": [
                    "project_goal",
                    "problem_statement",
                    "architecture",
                    "repository_structure",
                    "completed_components",
                    "current_progress",
                    "important_decisions",
                    "algorithms",
                    "datasets",
                    "experiments",
                    "code_modules",
                    "open_questions",
                    "next_steps",
                    "limitations"
                ]
            },
            "type": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["topic", "type", "content"]
    }
}

def generate_response(prompt: str):

    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": EXTRACTION_SCHEMA,
        "options": {
            "temperature": 0,
        }
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.text}")

    result = response.json()

    return json.loads(result["response"])