"""Inactive Ollama provider adapter."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NoReturn

from ravehunter.ai.provider import AIProvider, ClassificationResult
from ravehunter.domain.event import Event


class OllamaProvider(AIProvider):
    """Ollama placeholder; local model calls are intentionally disabled."""

    _disabled_message = (
        "OllamaProvider is not enabled. "
        "Define local runtime limits and security policy before use."
    )

    @classmethod
    def _disabled(cls) -> NoReturn:
        raise NotImplementedError(cls._disabled_message)

    def classify(self, content: str) -> ClassificationResult:
        self._disabled()

    def extract_event(self, content: str) -> Event:
        self._disabled()

    def enrich(self, event: Event) -> Event:
        self._disabled()

    def embeddings(self, texts: Sequence[str]) -> list[list[float]]:
        self._disabled()
