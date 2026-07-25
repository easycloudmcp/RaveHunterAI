from __future__ import annotations

from repositories.instagram_repository import InstagramRepository

from services import (
    InstagramEventParser,
    InstagramPostClassifier,
)


class InstagramEnrichmentPipeline:
    """
    Reads raw Instagram posts from SQLite,
    enriches them with AI,
    and (in the next sprint)
    stores detected events.
    """

    def __init__(self) -> None:

        self.repository = InstagramRepository()

        self.classifier = InstagramPostClassifier()
        self.event_parser = InstagramEventParser()

    def run(self) -> None:

        posts = self.repository.get_pending_posts()

        print(f"\nFound {len(posts)} pending Instagram posts\n")

        for post in posts:

            classification = self.classifier.classify(
                post.caption
            )

            parsed_event = self.event_parser.parse(
                post.caption
            )

            print("=" * 80)
            print(post.url)
            print("-" * 80)

            print(f"Category : {classification.category}")
            print(f"Title    : {parsed_event.title}")
            print(f"Date     : {parsed_event.event_date}")
            print(f"Time     : {parsed_event.start_time}")
            print(f"Venue    : {parsed_event.venue}")
            print(f"City     : {parsed_event.city}")
            print(f"Ticket   : {parsed_event.ticket_url}")

            #
            # Sprint 0.8.3
            #
            # self.event_repository.save(...)
            # self.repository.mark_processed(post.id)
            #