from playwright.sync_api import sync_playwright, Browser, Page


class ShotgunBrowser:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser: Browser = self.playwright.chromium.launch(
            headless=False
        )

    def open(self, url: str) -> Page:

        page = self.browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        return page

    def close(self):

        self.browser.close()

        self.playwright.stop()