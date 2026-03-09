import requests
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

def generate_response(prompt: str) -> str:

    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.text}")

    result = response.json()

    return result["response"]