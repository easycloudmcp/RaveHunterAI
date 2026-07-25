"""Factory for selecting a configured AI provider."""

from __future__ import annotations

from collections.abc import Callable

from ravehunter.ai.mock_provider import MockProvider
from ravehunter.ai.provider import AIProvider


class AIProviderFactory:
    """Create provider instances without exposing provider-specific setup."""

    _providers: dict[str, Callable[[], AIProvider]] = {
        "mock": MockProvider,
    }

    @classmethod
    def create(cls, provider: str = "mock") -> AIProvider:
        """Create an available provider by its case-insensitive name."""
        normalized = provider.strip().lower()

        try:
            provider_factory = cls._providers[normalized]
        except KeyError as error:
            available = ", ".join(sorted(cls._providers))
            raise ValueError(
                f"AI provider {provider!r} is not available. "
                f"Available providers: {available}."
            ) from error

        return provider_factory()
