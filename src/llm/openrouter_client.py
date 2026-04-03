import os

import requests
from dotenv import load_dotenv

load_dotenv()

_model_logged = False


def generate_response(prompt: str) -> str:
    global _model_logged

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file."
        )
    if not model:
        raise RuntimeError(
            "OPENROUTER_MODEL is not set. Add it to your .env file."
        )

    if not _model_logged:
        print(f"[INFO] Using OpenRouter model: {model}")
        _model_logged = True

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "ai-context-memory",
        "X-Title": "AI Context Memory",
    }

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=120,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenRouter request failed: {e}") from e

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter returned HTTP {response.status_code}: {response.text}"
        )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(
            f"Unexpected OpenRouter response shape: {response.text}"
        ) from e
