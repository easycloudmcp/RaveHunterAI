import sys

from collectors.instagram.browser import InstagramBrowser
from collectors.instagram.post_parser import InstagramPostParser


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "python -m collectors.instagram.test_post "
            "https://www.instagram.com/account/p/POST_ID/"
        )
        raise SystemExit(1)

    post_url = sys.argv[1]

    browser = InstagramBrowser()
    parser = InstagramPostParser()

    try:
        page = browser.open(post_url)
        post = parser.parse(page, post_url)

        print("\nInstagram Post")
        print("------------------------------")
        print(f"URL      : {post.url}")
        print(f"Published: {post.published_at or 'Not found'}")
        print(f"Image    : {post.image_url or 'Not found'}")
        print(f"Caption  : {post.caption or 'Not found'}")

    finally:
        browser.close()


if __name__ == "__main__":
    main()