from playwright.sync_api import sync_playwright
from pathlib import Path

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = browser.new_context(
        ignore_https_errors=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("Navigating...")
    page.goto("https://petrojam.com/price-schedule", timeout=30000)
    page.wait_for_timeout(4000)
    html = page.content()
    browser.close()

out = Path(__file__).parent / "petrojam_debug.html"
out.write_text(html, encoding="utf-8")
print(f"Saved {len(html)} chars to {out}")
print("Open scripts/petrojam_debug.html in a browser to inspect the layout.")
