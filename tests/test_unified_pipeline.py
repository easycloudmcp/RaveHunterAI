import sqlite3
from dataclasses import replace

import pytest

from database.database import create_tables
from ravehunter.ai.mock_provider import MockProvider
from ravehunter.discovery.pipeline import DiscoveryPipeline
from ravehunter.discovery.source import NormalizedSourceRecord
from ravehunter.domain.enums import EventSource
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
