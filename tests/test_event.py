from datetime import datetime

from ravehunter.domain.event import Event
from ravehunter.domain.enums import EventSource, EventStatus
from ravehunter.domain.location import Location
from ravehunter.domain.schedule import Schedule
from ravehunter.domain.venue import Venue


def test_empty_event_is_invalid():
    event = Event()

    assert event.is_valid is False

    assert "Missing title" in event.validate()

    assert "Missing venue" in event.validate()

    assert "Missing start date" in event.validate()


def test_valid_event():
    venue = Venue(
        name="Harry Klein",
        location=Location(
            city="Munich",
            country="Germany",
        ),
    )

    schedule = Schedule(
        start=datetime(2026, 8, 15, 22, 0),
    )

    event = Event(
        source=EventSource.INSTAGRAM,
        title="Techno Night",
        venue=venue,
        schedule=schedule,
    )

    assert event.is_valid

    assert event.validate() == []

    assert event.source == EventSource.INSTAGRAM


def test_publish():
    event = Event()

    event.publish()

    assert event.status == EventStatus.PUBLISHED


def test_archive():
    event = Event()

    event.archive()

    assert event.status == EventStatus.ARCHIVED


def test_cancel():
    event = Event()

    event.cancel()

    assert event.status == EventStatus.CANCELLED


def test_search_text():
    venue = Venue(
        name="Harry Klein",
        location=Location(),
    )

    schedule = Schedule(
        start=datetime.now(),
    )

    event = Event(
        title="Techno Night",
        description="Berlin style underground",
        venue=venue,
        schedule=schedule,
        tags=["warehouse"],
    )

    event.music.genres.append("Techno")

    event.music.artists.append("Ben Klock")

    text = event.search_text.lower()

    assert "techno night" in text

    assert "harry klein" in text

    assert "techno" in text

    assert "ben klock" in text

    assert "warehouse" in text


def test_duplicate_key_is_stable():
    venue = Venue(
        name="Harry Klein",
        location=Location(),
    )

    schedule = Schedule(
        start=datetime(2026, 8, 15, 22, 0),
    )

    event1 = Event(
        title="Techno Night",
        venue=venue,
        schedule=schedule,
    )

    event2 = Event(
        title="Techno Night",
        venue=venue,
        schedule=schedule,
    )

    assert event1.duplicate_key == event2.duplicate_key