import sys

from src.ingestion.fetch_share_link_http import fetch_share_page


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_http_fetch.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"[INFO] Fetching: {url}\n")

    try:
        html = fetch_share_page(url)
        print(f"[OK] Successfully fetched {len(html)} characters of HTML.")
        print("\n--- First 500 characters ---")
        print(html[:500])
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
