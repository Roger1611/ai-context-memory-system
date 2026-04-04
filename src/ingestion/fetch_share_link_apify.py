import os

import requests
from dotenv import load_dotenv

load_dotenv()

_ACTOR_ENDPOINT = (
    "https://api.apify.com/v2/acts/klinzinger~chatgpt-conversation-extractor"
    "/run-sync-get-dataset-items"
)

# 270 s — safely under Apify's 300 s hard sync limit
_REQUEST_TIMEOUT = 270


def fetch_share_page(url: str) -> list[dict]:
    api_token = os.getenv("APIFY_TOKEN")
    if not api_token:
        raise RuntimeError(
            "APIFY_TOKEN is not set. Add it to your .env file."
        )

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    body = {
        "startUrls": [{"url": url}],
        "includeRawData": False,
    }

    try:
        response = requests.post(
            _ACTOR_ENDPOINT,
            headers=headers,
            json=body,
            timeout=_REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Apify actor timed out after {_REQUEST_TIMEOUT}s for URL: {url}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Apify request failed for URL: {url} — {e}") from e

    if not response.ok:
        raise RuntimeError(
            f"Apify returned HTTP {response.status_code} for URL: {url} — {response.text}"
        )

    try:
        results = response.json()
    except ValueError as e:
        raise RuntimeError(
            f"Apify response is not valid JSON for URL: {url} — {response.text[:200]}"
        ) from e

    if not results:
        raise RuntimeError(
            f"Apify returned an empty dataset for URL: {url}. "
            "The share link may be invalid or the conversation is not publicly accessible."
        )

    first = results[0]
    raw_messages = first.get("messages")

    if raw_messages is None:
        raise RuntimeError(
            f"Apify result is missing 'messages' field for URL: {url}. "
            f"Available keys: {list(first.keys())}"
        )

    if not raw_messages:
        raise RuntimeError(
            f"Apify returned an empty 'messages' list for URL: {url}."
        )

    try:
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in raw_messages
        ]
    except KeyError as e:
        raise RuntimeError(
            f"Apify message item is missing expected field {e} for URL: {url}"
        ) from e

    return messages
