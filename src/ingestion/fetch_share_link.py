from playwright.sync_api import sync_playwright


def fetch_share_page(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            print(f"[INFO] Opening share link: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            html = page.content()
            return html
        except Exception as e:
            raise RuntimeError(f"Failed to fetch share link: {url} — {e}") from e
        finally:
            browser.close()
