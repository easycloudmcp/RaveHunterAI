from services.instagram_event_parser import InstagramEventParser


TEST_CAPTION = """
Techno Open Air München

19.07.2026
Doors 14:00 Uhr

Join us for a full day of melodic techno.

Tickets:
https://shotgun.live/events/techno-open-air

See you on the dancefloor.
"""


def main() -> None:
    parser = InstagramEventParser()

    event = parser.parse(TEST_CAPTION)

    print("\nParsed Event")
    print("-" * 40)
    print(f"Title : {event.title}")
    print(f"Date  : {event.date}")
    print(f"Time  : {event.time}")
    print(f"City  : {event.city}")
    print(f"URL   : {event.ticket_url}")


if __name__ == "__main__":
    main()