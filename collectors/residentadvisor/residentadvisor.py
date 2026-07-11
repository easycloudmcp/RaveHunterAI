from pathlib import Path

from playwright.sync_api import sync_playwright

from rich.console import Console

console = Console()


class ResidentAdvisorCollector:

    URL = "https://ra.co/events/de"

    def collect(self):

        profile = Path.home() / ".ravehunter"

        with sync_playwright() as p:

            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                headless=False,
                slow_mo=100,
                viewport={"width": 1600, "height": 1000},
            )

            page = browser.new_page()

            page.goto(self.URL)

            input(
                "\nSolve any challenge.\n"
                "Browse until you see the event list.\n"
                "Then press ENTER here..."
            )

            print(page.title())

            browser.close()

        return []