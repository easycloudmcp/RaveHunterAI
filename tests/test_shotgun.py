from collectors.shotgun.parser import ShotgunParser


class FakePage:
    def title(self) -> str:
        return "Fixture Event"


def test_shotgun_parser_maps_page_to_event() -> None:
    event = ShotgunParser().parse(
        FakePage(),  # type: ignore[arg-type]
        "https://example.test/events/fixture",
    )

    assert event.event_name == "Fixture Event"
    assert event.source == "Shotgun"
    assert event.ticket_url == "https://example.test/events/fixture"
