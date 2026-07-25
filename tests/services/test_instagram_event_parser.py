from services.instagram_event_parser import InstagramEventParser


def test_parses_event_fields_from_caption() -> None:
    caption = """
    Techno Open Air München

    19.07.2026
    Doors 14:00 Uhr

    Tickets:
    https://shotgun.live/events/techno-open-air
    """
    parser = InstagramEventParser()
    event = parser.parse(caption)

    assert event.title == "Techno Open Air München"
    assert event.date == "19.07.2026"
    assert event.time == "14:00"
    assert event.city == "München"
    assert event.ticket_url == (
        "https://shotgun.live/events/techno-open-air"
    )
