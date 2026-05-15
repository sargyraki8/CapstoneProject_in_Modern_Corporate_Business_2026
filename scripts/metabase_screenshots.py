#!/usr/bin/env python
# Uses Playwright to log into Metabase, open each Question created by
# metabase_setup.py, wait for the query to finish, and save a PNG screenshot.
#
# Output: D:/Projects/Capstone/screenshots/metabase_q{1-4}.png

import json
import time
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
CREDS_FILE = REPO_ROOT / "exports" / "metabase_creds.json"
SCREENSHOT_DIR = REPO_ROOT / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

creds = json.loads(CREDS_FILE.read_text())
URL = creds["url"]
EMAIL = creds["email"]
PASSWORD = creds["password"]
CARD_IDS = creds["card_ids"]
CARD_NAMES = creds["card_names"]


def wait_for_results(page):
    if page.locator("text=To run your code").first.is_visible():
        try:
            page.click('button:has-text("Run")', timeout=5000)
        except Exception:
            page.keyboard.press("Control+Enter")

    page.wait_for_load_state("networkidle")
    page.wait_for_selector(
        '[data-testid="query-visualization-root"], .Visualization, table tbody tr, [data-testid="TableInteractive-root"]',
        timeout=60000,
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()

        print(f"Opening {URL}/auth/login")
        page.goto(f"{URL}/auth/login", wait_until="networkidle")

        # Metabase login form
        page.fill('input[name="username"]', EMAIL)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        print("Logged in.")

        for i, (card_id, name) in enumerate(zip(CARD_IDS, CARD_NAMES), start=1):
            url = f"{URL}/question/{card_id}"
            print(f"[{i}/4] Opening {name}  ->  {url}")
            page.goto(url, wait_until="networkidle")

            # Let the native query run and the result render.
            try:
                wait_for_results(page)
            except Exception:
                time.sleep(5)

            # Dismiss "It's okay to play around with saved questions" modal
            # and any similar first-view modals.
            try:
                page.click('text="Start exploring"', timeout=2000)
                time.sleep(1)
            except Exception:
                pass
            try:
                # Fallback: press Escape twice to close any modal
                page.keyboard.press("Escape")
                page.keyboard.press("Escape")
            except Exception:
                pass

            try:
                wait_for_results(page)
            except Exception:
                time.sleep(3)

            out = SCREENSHOT_DIR / f"metabase_q{i}.png"
            page.screenshot(path=str(out), full_page=True)
            print(f"  Saved {out}")

        browser.close()
    print(f"\nDone. Screenshots in {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
