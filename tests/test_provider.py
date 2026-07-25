from collections.abc import Sequence

import pytest

from ravehunter.ai.provider import AIProvider, ClassificationResult
from ravehunter.domain.event import Event


class CompleteProvider(AIProvider):
    def classify(self, content: str) -> ClassificationResult:
        return ClassificationResult(
            label="event",
            confidence=1.0,
            reason=content,
        )

    def extract_event(self, content: str) -> Event:
        return Event(title=content)

    def enrich(self, event: Event) -> Event:
        return event

    def embeddings(self, texts: Sequence[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]


class IncompleteProvider(AIProvider):
    def classify(self, content: str) -> ClassificationResult:
        return ClassificationResult(label=content, confidence=1.0)


def test_ai_provider_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        AIProvider()  # type: ignore[abstract]


def test_every_provider_must_implement_the_complete_contract() -> None:
    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_complete_provider_uses_normalized_contract_types() -> None:
    provider = CompleteProvider()
    event = provider.extract_event("Techno Night")

    assert provider.classify("announcement") == ClassificationResult(
        label="event",
        confidence=1.0,
        reason="announcement",
    )
    assert event.title == "Techno Night"
    assert provider.enrich(event) is event
    assert provider.embeddings(["one", "four"]) == [[3.0], [4.0]]
