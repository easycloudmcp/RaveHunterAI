import sqlite3
from dataclasses import replace

import pytest

from database.database import create_tables
from ravehunter.ai.mock_provider import MockProvider
from ravehunter.discovery.pipeline import DiscoveryPipeline
from ravehunter.discovery.source import NormalizedSourceRecord
from ravehunter.domain.enums import EventSource, EventStatus
from ravehunter.domain.event import Event
from repositories.event_repository import EventRepository


@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")
    create_tables(connection)
    return EventRepository(connection)


def record(external_id="meta-1"):
    return NormalizedSourceRecord(
        source=EventSource.INSTAGRAM,
        account_id="account-1",
        media_id=external_id,
        caption="Rave Night\nMünchen",
        media_type="IMAGE",
        media_url=None,
        permalink=f"https://instagram.com/p/{external_id}",
        raw_evidence_reference=f"file:///evidence/{external_id}.json",
    )


def test_complete_vertical_slice(repository):
    result = DiscoveryPipeline(MockProvider(), repository).run([record()])
    assert result.persisted == 1
    saved = repository.list(city="Munich")
    assert len(saved) == 1
    assert saved[0].title == "Rave Night"
    assert saved[0].classification_label == "event"
    assert saved[0].confidence.value == 1.0
    assert saved[0].raw_source_id == "meta-1"


def test_duplicate_prevention(repository):
    pipeline = DiscoveryPipeline(MockProvider(), repository)
    assert pipeline.run([record()]).persisted == 1
    result = pipeline.run([record()])
    assert result.duplicates == 1
    assert len(repository.all()) == 1


def test_repository_get_and_city_query(repository):
    DiscoveryPipeline(MockProvider(), repository).run([record()])
    event = repository.all()[0]
    assert repository.get(str(event.id)) == event
    assert repository.list(city="Berlin") == []


def test_query_by_city_with_umlaut(repository):
    provider = MockProvider()
    original = provider.extract_event

    def extract(content):
        event = original(content)
        assert event.venue is not None
        event.venue.location.city = "München"
        return event

    provider.extract_event = extract
    DiscoveryPipeline(provider, repository).run([record()])
    assert len(repository.list(city="München")) == 1


class InvalidProvider(MockProvider):
    def extract_event(self, content):
        return Event(title="Incomplete")


def test_invalid_event_rejected(repository):
    result = DiscoveryPipeline(InvalidProvider(), repository).run([record()])
    assert result.rejected == 1
    assert result.persisted == 0


class NonEventProvider(MockProvider):
    def classify(self, content):
        return replace(
            super().classify(content),
            label="other",
            reason="No event evidence.",
        )


def test_non_event_is_not_extracted(repository):
    result = DiscoveryPipeline(NonEventProvider(), repository).run([record()])
    assert result.rejected == 1
    assert repository.all() == []


def test_repository_rejects_invalid_event(repository):
    with pytest.raises(ValueError, match="Missing venue"):
        repository.insert(Event(title="No venue"))


@pytest.mark.parametrize(
    "status",
    [
        EventStatus.DISCOVERED,
        EventStatus.VALIDATED,
        EventStatus.PUBLISHED,
        EventStatus.ARCHIVED,
        EventStatus.CANCELLED,
    ],
)
def test_repository_round_trip_preserves_canonical_event(repository, status):
    event = replace(
        MockProvider().extract_event(f"{status.value} event"),
        status=status,
        external_id=f"external-{status.value}",
        raw_source_id=f"raw-{status.value}",
        raw_evidence_refs=[
            f"file:///evidence/{status.value}-one.json",
            f"file:///evidence/{status.value}-two.json",
        ],
    )
    expected_duplicate_key = event.duplicate_key

    assert repository.insert(event) is True
    assert repository.insert(event) is False

    loaded_by_id = repository.get(str(event.id))
    loaded_by_list = next(
        listed for listed in repository.list() if listed.id == event.id
    )
    for loaded in (loaded_by_id, loaded_by_list):
        assert loaded is not None
        assert loaded.status is status
        assert loaded.id == event.id
        assert loaded.source is event.source
        assert loaded.external_id == event.external_id
        assert loaded.raw_source_id == event.raw_source_id
        assert loaded.raw_evidence_refs == event.raw_evidence_refs
        assert loaded.created == event.created
        assert loaded.updated == event.updated
        assert loaded.duplicate_key == expected_duplicate_key


def test_repository_rejects_unknown_persisted_status(repository):
    event = MockProvider().extract_event("Malformed status event")
    assert repository.insert(event) is True
    repository.connection.execute(
        "UPDATE canonical_events SET processing_state = ? WHERE id = ?",
        ("unknown-status", str(event.id)),
    )
    repository.connection.commit()

    with pytest.raises(ValueError, match="unknown-status"):
        repository.get(str(event.id))
    with pytest.raises(ValueError, match="unknown-status"):
        repository.list()
