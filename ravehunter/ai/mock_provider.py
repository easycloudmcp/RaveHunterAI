"""Deterministic AI provider for local development and tests."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime

from ravehunter.ai.provider import AIProvider, ClassificationResult
from ravehunter.domain.enums import EventSource
from ravehunter.domain.event import Event
from ravehunter.domain.location import Location
from ravehunter.domain.schedule import Schedule
from ravehunter.domain.venue import Venue


class MockProvider(AIProvider):
    """Return deterministic results without calling an external service."""

    def classify(self, content: str) -> ClassificationResult:
        if not content.strip():
            return ClassificationResult(
                label="other",
                confidence=1.0,
                reason="Mock provider received empty content.",
            )

        return ClassificationResult(
            label="event",
            confidence=1.0,
            reason="Deterministic mock classification.",
        )

    def extract_event(self, content: str) -> Event:
        title = next(
            (
                line.strip()
                for line in content.splitlines()
                if line.strip()
            ),
            "Mock Event",
        )

        return Event(
            source=EventSource.MANUAL,
            external_id="mock-event",
            title=title,
            description=content.strip(),
            venue=Venue(
                name="Mock Venue",
                location=Location(
                    city="Munich",
                    country="Germany",
                ),
            ),
            schedule=Schedule(
                start=datetime(2026, 1, 1, 22, 0, tzinfo=UTC),
            ),
            tags=["mock"],
        )

    def enrich(self, event: Event) -> Event:
        tags = list(event.tags)

        if "mock-enriched" not in tags:
            tags.append("mock-enriched")

        return replace(event, tags=tags)

    def embeddings(self, texts: Sequence[str]) -> list[list[float]]:
        return [
            [
                float(len(text)),
                float(sum(ord(character) for character in text) % 1000),
            ]
            for text in texts
        ]
