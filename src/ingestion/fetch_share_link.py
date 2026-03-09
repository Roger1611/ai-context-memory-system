
#Responsible for loading AI conversation share links using a headless browser.


from playwright.sync_api import sync_playwright


def fetch_share_page(url: str) -> str:


    with sync_playwright() as p:

        # Launch Chromium browser in headless mode
        browser = p.chromium.launch(headless=True)

        # Create a new browser page
        page = browser.new_page()

        print(f"[INFO] Opening share link: {url}")

        # Navigate to the share page
        page.goto(url, wait_until="networkidle")

        # Extract the full HTML after page render
        html = page.content()

        browser.close()

        return html