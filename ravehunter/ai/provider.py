"""Provider-independent contract for RaveHunter AI capabilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from ravehunter.domain.event import Event


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Normalized classification returned by every AI provider."""

    label: str
    confidence: float
    reason: str = ""


class AIProvider(ABC):
    """Contract implemented by local, cloud, and test AI providers."""

    @abstractmethod
    def classify(self, content: str) -> ClassificationResult:
        """Classify unstructured content."""

    @abstractmethod
    def extract_event(self, content: str) -> Event:
        """Extract a canonical event from unstructured content."""

    @abstractmethod
    def enrich(self, event: Event) -> Event:
        """Return an event enriched with provider-derived information."""

    @abstractmethod
    def embeddings(self, texts: Sequence[str]) -> list[list[float]]:
        """Create one embedding vector for each supplied text."""
