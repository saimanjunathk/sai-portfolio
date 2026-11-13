import sys
from playwright.sync_api import sync_playwright

APPS = [
    "https://real-time-market-pipeline.streamlit.app/",
    "https://elt-data-warehouse.streamlit.app/",
    "https://quant-factor-research.streamlit.app/",
    "https://llm-data-platform.streamlit.app/",
    "https://ml-feature-store.streamlit.app/",
    "https://order-book-analysis.streamlit.app/",
]

WAKE_BUTTON = "Yes, get this app back up!"


def visit(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(5_000)

    status = "AWAKE"
    button = page.get_by_role("button", name=WAKE_BUTTON)
    if button.count() > 0:
        button.first.click()
        status = "WOKE"
        # the button disappears once the app starts booting
        button.first.wait_for(state="hidden", timeout=180_000)

    # wait for the app frame to load, but do not fail if the selector changes
    try:
        page.wait_for_selector('iframe[title="streamlitApp"]', timeout=180_000)
    except Exception:
        print(f"  note: app frame not detected for {url}")

    # stay on the page so the WebSocket session registers as traffic
    page.wait_for_timeout(20_000)
    return status


def main():
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in APPS:
            context = browser.new_context()
            page = context.new_page()
            try:
                status = visit(page, url)
                print(f"{status:6} {url}")
            except Exception as exc:
                print(f"FAILED {url} -> {exc}")
                failures.append(url)
            finally:
                context.close()
        browser.close()

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
