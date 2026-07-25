from collectors.instagram.browser import InstagramBrowser

POST = "https://www.instagram.com/blitzclub/p/BArmC1CDQI3/"


def main():

    browser = InstagramBrowser()

    try:

        page = browser.open(POST)

        page.wait_for_timeout(5000)

        print(page.content())

    finally:

        browser.close()


if __name__ == "__main__":
    main()