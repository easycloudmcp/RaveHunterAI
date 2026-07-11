from playwright.sync_api import sync_playwright
from rich.console import Console

console = Console()


class ResidentAdvisorCollector:

    URL = "https://ra.co/events/de"

    def collect(self):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False,
                slow_mo=300
            )

            page = browser.new_page()

            page.goto(self.URL)

            input("Press ENTER to continue...")

            browser.close()

        return []