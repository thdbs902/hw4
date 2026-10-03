"""Problem 11: take app-check screenshots of the running site (front end :5174, backend :8000).

Run from backend/:  .venv/bin/python app_check_screens.py
Uses the installed Google Chrome through Playwright (channel="chrome"). Browses as a guest,
so nothing is written to the database. Saves PNGs to output/app_check_images/.
"""

from pathlib import Path

from playwright.sync_api import Page, sync_playwright

SITE = "http://127.0.0.1:5174"
OUT = Path(__file__).resolve().parent.parent / "output" / "app_check_images"


def ask(page: Page, text: str) -> None:
    """Type into the DD chat like a shopper and wait for the real agent reply."""
    if not page.locator(".chat-panel").count():
        page.click(".chat-launcher")
    before = page.locator(".bubble").count()
    page.fill(".chat-form input", text)
    page.click(".chat-form button")
    page.wait_for_function(
        "n => document.querySelectorAll('.bubble').length >= n + 2 && !document.querySelector('.bubble.typing')",
        arg=before,
        timeout=90_000,
    )
    page.wait_for_timeout(1200)  # let cards finish their entrance animation


def shot(page: Page, name: str) -> None:
    page.screenshot(path=str(OUT / name))
    print("saved", name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)

        # 0. Home page (halftime design)
        page.goto(SITE + "/")
        page.wait_for_selector(".float-card img")
        page.wait_for_timeout(1500)
        shot(page, "home.png")

        # 1. Chat checks the inventory level of an item
        ask(page, "How many 2025 Yale vs Harvard T-shirts do you have in size L, and how much are they?")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        shot(page, "inventory.png")

        # 2. Category question -> dynamic search-result cards
        page.goto(SITE + "/")
        ask(page, "what hoodies do you have?")
        page.evaluate("window.scrollTo(0, 0)")  # panel sits at the top, under the nav
        page.wait_for_timeout(800)
        shot(page, "search_cards.png")

        # 3. Problem 9 front end: stock badges on product cards
        page.goto(SITE + "/products")
        page.wait_for_selector(".card .stock-badge")
        page.evaluate("window.scrollTo(0, 260)")
        page.wait_for_timeout(1200)
        shot(page, "stock_badges.png")

        # 4. Problem 9 front end: "Ask DD about this" button on a product page
        page.goto(SITE + "/products/yale-mom-hoodie")
        page.wait_for_selector(".ask-dd-chips button")
        page.click(".size:nth-child(3)")  # select M
        page.click(".ask-dd-chips button:first-child")  # "Is this in M?"
        page.wait_for_function(
            "() => document.querySelectorAll('.bubble').length >= 3 && !document.querySelector('.bubble.typing')",
            timeout=90_000,
        )
        page.wait_for_timeout(1000)
        page.locator(".ask-dd").scroll_into_view_if_needed()
        shot(page, "ask_dd.png")

        # 5. Problem 9 agent: sold-out size -> find_alternatives cards
        page.goto(SITE + "/products/baseball-left-chest-crewneck")
        page.wait_for_selector(".detail h1")
        ask(page, "Is this in XL?")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        shot(page, "alternatives.png")

        browser.close()


if __name__ == "__main__":
    main()
