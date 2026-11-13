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

    button = page.get_by_role("button", name=WAKE_BUTTON)
    frame = page.locator('iframe[title="streamlitApp"]')

    # wait up to 30s for whichever shows first: wake button or app frame
    try:
        button.or_(frame).first.wait_for(timeout=30_000)
    except Exception:
        pass

    status = "AWAKE"
    if button.count() > 0:
        button.first.click()
        status = "WOKE"
        button.first.wait_for(state="hidden", timeout=180_000)

    try:
        frame.first.wait_for(timeout=180_000)
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
