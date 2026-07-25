from pathlib import Path

from collectors.instagram.browser import InstagramBrowser

PROFILE = "https://www.instagram.com/verknipt/"


def main():

    browser = InstagramBrowser()

    try:
        page = browser.open(PROFILE)

        page.wait_for_timeout(8000)

        html = page.content()

        Path("debug").mkdir(exist_ok=True)
        Path("debug/verknipt.html").write_text(
            html,
            encoding="utf-8"
        )

        page.screenshot(path="debug/verknipt.png", full_page=True)

        print("HTML written to debug/verknipt.html")
        print("Screenshot written to debug/verknipt.png")

    finally:
        browser.close()


if __name__ == "__main__":
    main()