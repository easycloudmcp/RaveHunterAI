from database.database import Database
from models import Event
from repositories.event_repository import EventRepository


def test_database_and_event_repository_round_trip(tmp_path) -> None:
    database = Database(tmp_path / "ravehunter.db")
    database.create_tables()
    repository = EventRepository(database.connection)
    event = Event(
        event_name="Deterministic Techno Night",
        city="Munich",
        ticket_url="https://example.test/events/1",
        source="fixture",
    )

    assert repository.insert(event) is True
    assert repository.insert(event) is False
    assert repository.all() == [event]

    database.close()


def test_event_requires_identity_fields() -> None:
    event = Event(event_name="Test Event", source="fixture")

    assert event.event_name == "Test Event"
    assert event.source == "fixture"
