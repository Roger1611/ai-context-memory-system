import requests


def fetch_share_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"HTTP error fetching share link: {url} — {e.response.status_code} {e.response.reason}"
        ) from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Connection error fetching share link: {url} — {e}") from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"Timeout fetching share link: {url} — {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch share link: {url} — {e}") from e
