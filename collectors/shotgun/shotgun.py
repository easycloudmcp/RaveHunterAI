from playwright.sync_api import Page

from models import Event

from .browser import ShotgunBrowser
from .parser import ShotgunParser


class ShotgunCollector:

    URL = "https://shotgun.live/en"

    def __init__(self):

        self.browser = ShotgunBrowser()

        self.parser = ShotgunParser()

    @staticmethod
    def dismiss_cookie_banner(page: Page):

        selectors = [
            "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            "#CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll",
            "button:has-text('Allow all')",
            "button:has-text('Accept all')",
            "button:has-text('Reject all')",
        ]

        for selector in selectors:

            try:

                button = page.locator(selector).first

                if button.is_visible(timeout=1500):

                    button.click()

                    page.wait_for_timeout(1500)

                    print(f"Cookie banner dismissed using {selector}")

                    return

            except Exception:

                pass

        print("No clickable cookie banner button found.")

    def discover_links(self, page: Page) -> list[dict]:

        page.wait_for_timeout(4000)

        for _ in range(4):

            page.mouse.wheel(0, 1200)

            page.wait_for_timeout(1000)

        return page.locator("a[href]").evaluate_all(
            """
            elements => elements
                .map(anchor => ({
                    text: (anchor.innerText || "").trim(),
                    href: anchor.href
                }))
                .filter(item =>
                    item.text &&
                    item.href &&
                    item.href.includes("/events/")
                )
            """
        )

    def collect(self) -> list[Event]:

        homepage = self.browser.open(self.URL)

        self.dismiss_cookie_banner(homepage)

        print(f"Title: {homepage.title()}")

        links = self.discover_links(homepage)

        events: list[Event] = []

        seen = set()

        #
        # Sprint 0.5
        #
        # For now
        # only create Event objects.
        #
        # Next sprint
        # parser.parse(...)
        #

        for link in links:

            url = link["href"]

            if url in seen:
                continue

            seen.add(url)

            text = link["text"].strip()

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            event_name = (
                lines[0]
                if lines
                else "Unknown Event"
            )

            events.append(
                Event(
                    event_name=event_name,
                    ticket_url=url,
                    source="Shotgun",
                )
            )

        self.browser.close()

        return events