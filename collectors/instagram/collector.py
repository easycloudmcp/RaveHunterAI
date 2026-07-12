from __future__ import annotations

from playwright.sync_api import Page

from collectors.instagram.models import InstagramPost
from collectors.instagram.parser import InstagramParser
from collectors.instagram.post_parser import InstagramPostParser

from repositories.instagram_repository import InstagramRepository

from services import (
    InstagramEventParser,
    InstagramPostClassifier,
)


class InstagramCollector:

    def __init__(self) -> None:

        self.parser = InstagramParser()
        self.post_parser = InstagramPostParser()

        self.classifier = InstagramPostClassifier()
        self.event_parser = InstagramEventParser()

        self.repository = InstagramRepository()

    def collect(
        self,
        page: Page,
        limit: int = 12,
    ) -> list[InstagramPost]:

        posts: list[InstagramPost] = []

        urls = self.parser.extract_post_urls(
            page,
            limit=limit,
        )

        for url in urls:

            print(f"Opening {url}")

            page.goto(
                url,
                wait_until="networkidle",
            )

            html = page.content()

            caption = self.post_parser.extract_caption(
                html
            )

            post_date = self.parser.extract_post_date(
                page
            )

            classification = self.classifier.classify(
                caption
            )

            parsed_event = self.event_parser.parse(
                caption
            )

            post = InstagramPost(
                url=url,
                caption=caption,
                post_date=post_date,
                category=classification.category,
                parsed_event=parsed_event,
            )

            self.repository.save_post(post)

            posts.append(post)

        return posts