from playwright.sync_api import Page, TimeoutError, sync_playwright

from models import Event


class ShotgunCollector:

    URL = "https://shotgun.live/en"

    @staticmethod
    def dismiss_cookie_banner(page: Page) -> None:

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
                    print(f"Cookie banner dismissed using: {selector}")
                    return

            except TimeoutError:
                pass

        print("No clickable cookie banner button found.")

    def collect(self) -> list[Event]:

        events: list[Event] = []

        seen_urls: set[str] = set()

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=False
            )

            page = browser.new_page(
                viewport={
                    "width": 1440,
                    "height": 1000,
                }
            )

            page.goto(
                self.URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            self.dismiss_cookie_banner(page)

            page.wait_for_timeout(4000)

            for _ in range(4):
                page.mouse.wheel(0, 1200)
                page.wait_for_timeout(1000)

            print(f"Title: {page.title()}")
            print(f"URL: {page.url}")

            links = page.locator("a[href]").evaluate_all(
                """
                elements => elements
                    .map(anchor => ({
                        text: (anchor.innerText || "").trim(),
                        href: anchor.href
                    }))
                    .filter(item =>
                        item.text &&
                        item.href &&
                        (
                            item.href.includes("/events/")
                        )
                    )
                """
            )

            for link in links:

                url = link["href"]

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                raw_text = link["text"].strip()

                lines = [
                    line.strip()
                    for line in raw_text.splitlines()
                    if line.strip()
                ]

                event_name = (
                    lines[0]
                    if lines
                    else "Unknown Event"
                )

                event = Event(
                    event_name=event_name,
                    ticket_url=url,
                    source="Shotgun",
                )

                #
                # Sprint 0.5
                #
                # Next sprint we visit the event page
                # and populate:
                #
                # venue
                # date
                # price
                # genre
                # description
                #

                events.append(event)

            browser.close()

        return events