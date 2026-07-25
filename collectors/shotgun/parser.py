from playwright.sync_api import Page

from models import Event


class ShotgunParser:

    def parse(
        self,
        page: Page,
        url: str,
    ) -> Event:

        title = page.title()

        print("\n----------------------------")
        print("EVENT PAGE")
        print("----------------------------")
        print(title)
        print(url)
        print("----------------------------\n")

        return Event(
            event_name=title,
            ticket_url=url,
            source="Shotgun",
        )