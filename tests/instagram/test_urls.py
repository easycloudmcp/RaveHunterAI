from collectors.instagram.browser import InstagramBrowser
from collectors.instagram.parser import InstagramParser


PROFILE = "https://www.instagram.com/verknipt/"


def main():

    browser = InstagramBrowser()

    try:

        page = browser.open(PROFILE)

        page.wait_for_timeout(5000)

        parser = InstagramParser()

        urls = parser.extract_post_urls(
            page,
            limit=20,
        )

        print()

        print(f"Found {len(urls)} URLs")

        print()

        for url in urls:
            print(url)

    finally:

        browser.close()


if __name__ == "__main__":
    main()