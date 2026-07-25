from datetime import UTC, datetime

from ravehunter.ai.mock_provider import MockProvider
from ravehunter.domain.event import Event


def test_mock_provider_classification_is_deterministic() -> None:
    provider = MockProvider()

    assert provider.classify("Techno Night").label == "event"
    assert provider.classify("Techno Night").confidence == 1.0
    assert provider.classify("   ").label == "other"


def test_mock_provider_extracts_valid_fixture_event() -> None:
    event = MockProvider().extract_event(
        "Techno Night\nA deterministic fixture event."
    )

    assert event.title == "Techno Night"
    assert event.description == (
        "Techno Night\nA deterministic fixture event."
    )
    assert event.venue is not None
    assert event.venue.name == "Mock Venue"
    assert event.venue.location.city == "Munich"
    assert event.schedule.start == datetime(
        2026,
        1,
        1,
        22,
        0,
        tzinfo=UTC,
    )
    assert event.is_valid


def test_mock_provider_enriches_without_mutating_input() -> None:
    source = Event(title="Techno Night", tags=["fixture"])

    enriched = MockProvider().enrich(source)

    assert source.tags == ["fixture"]
    assert enriched.tags == ["fixture", "mock-enriched"]
    assert MockProvider().enrich(enriched).tags == [
        "fixture",
        "mock-enriched",
    ]


def test_mock_provider_embeddings_are_repeatable() -> None:
    provider = MockProvider()

    first = provider.embeddings(["abc", ""])
    second = provider.embeddings(["abc", ""])

    assert first == second
    assert first == [[3.0, 294.0], [0.0, 0.0]]
