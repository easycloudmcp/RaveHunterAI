from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright


class InstagramBrowser:

    def __init__(self):

        self.profile = Path.home() / ".ravehunter-instagram"

        self.playwright = sync_playwright().start()

        self.context: BrowserContext = (
            self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile),
                headless=False,
                slow_mo=100,
                viewport={
                    "width": 1440,
                    "height": 1000,
                },
            )
        )

    def open(self, url: str) -> Page:

        page = self.context.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        return page

    def close(self):

        self.context.close()

        self.playwright.stop()