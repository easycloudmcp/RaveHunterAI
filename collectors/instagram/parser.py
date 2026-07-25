from __future__ import annotations

from playwright.sync_api import Page


class InstagramParser:
    """
    Responsible for extracting information from Instagram pages.

    This class only parses the HTML/DOM.

    It does NOT:
        - classify posts
        - create Event objects
        - write to SQLite

    Those responsibilities belong to the service layer.
    """

    def extract_post_urls(
        self,
        page: Page,
        limit: int = 12,
    ) -> list[str]:
        """
        Extract unique Instagram post and reel URLs from a profile page.
        """

        page.wait_for_timeout(3000)

        links = page.locator(
            'a[href*="/p/"], a[href*="/reel/"]'
        ).evaluate_all(
            """
            elements => elements.map(element => element.href)
            """
        )

        unique_urls: list[str] = []
        seen: set[str] = set()

        for url in links:

            clean_url = url.split("?")[0]

            if clean_url in seen:
                continue

            seen.add(clean_url)
            unique_urls.append(clean_url)

            if len(unique_urls) >= limit:
                break

        return unique_urls

    def extract_caption(
        self,
        page: Page,
    ) -> str:
        """
        Extract the caption from an Instagram post.

        Instagram changes its HTML frequently, so we try multiple selectors.
        """

        page.wait_for_timeout(1500)

        selectors = [
            "article h1",
            'div[role="dialog"] h1',
            "h1",
        ]

        for selector in selectors:

            locator = page.locator(selector)

            if locator.count() == 0:
                continue

            try:
                caption = locator.first.inner_text().strip()

                if caption:
                    return caption

            except Exception:
                pass

        return ""

    def extract_post_date(
        self,
        page: Page,
    ) -> str:
        """
        Extract the ISO datetime from an Instagram post.

        Returns an empty string if unavailable.
        """

        try:

            locator = page.locator("time")

            if locator.count() == 0:
                return ""

            datetime_value = locator.first.get_attribute("datetime")

            return datetime_value or ""

        except Exception:
            return ""

    def extract_location(
        self,
        page: Page,
    ) -> str:
        """
        Placeholder for future location extraction.
        """

        return ""

    def extract_hashtags(
        self,
        caption: str,
    ) -> list[str]:
        """
        Extract hashtags from a caption.
        """

        hashtags: list[str] = []

        for word in caption.split():

            if word.startswith("#"):

                hashtags.append(
                    word.rstrip(".,!?;:")
                )

        return hashtags