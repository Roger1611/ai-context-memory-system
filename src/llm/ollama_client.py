import requests

from src.config import OLLAMA_BASE_URL


class OllamaError(Exception):
    pass


def _raise_for_ollama_error(response):
    if response.status_code == 200:
        return

    try:
        payload = response.json()
        message = payload.get("error") or response.text
    except ValueError:
        message = response.text

    raise OllamaError(message)


def generate_response(prompt: str, model: str, timeout=120):
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise OllamaError(str(exc)) from exc
    _raise_for_ollama_error(response)
    return response.json()["response"]


def list_local_models():
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        raise OllamaError(str(exc)) from exc
    _raise_for_ollama_error(response)
    payload = response.json()
    return payload.get("models", [])
