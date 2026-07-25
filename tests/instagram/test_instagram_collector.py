from __future__ import annotations

from collectors.instagram.browser import InstagramBrowser
from collectors.instagram.collector import InstagramCollector
from collectors.instagram.profiles import PROMOTERS


PROFILE = PROMOTERS[0]


def main() -> None:

    browser = InstagramBrowser()

    try:

        page = browser.open(PROFILE)

        collector = InstagramCollector()

        posts = collector.collect(
            page,
            limit=5,
        )

        print("\nCollected Posts")
        print("=" * 80)

        for post in posts:

            print("\n" + "=" * 80)
            print("CAPTION")
            print("-" * 80)
            print(post.caption)
            print("=" * 80)

            print(f"URL       : {post.url}")
            print(f"Category  : {post.category}")
            print(f"Post Date : {post.post_date}")

            if post.parsed_event:

                event = post.parsed_event

                print(f"Title     : {event.title}")
                print(f"Date      : {event.date}")
                print(f"Time      : {event.time}")
                print(f"City      : {event.city}")
                print(f"Ticket    : {event.ticket_url}")

    finally:

        browser.close()


if __name__ == "__main__":
    main()