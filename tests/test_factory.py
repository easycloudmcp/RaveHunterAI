import pytest

from ravehunter.ai.factory import AIProviderFactory
from ravehunter.ai.mock_provider import MockProvider
from ravehunter.ai.provider import AIProvider


def test_factory_defaults_to_mock_provider() -> None:
    provider = AIProviderFactory.create()

    assert isinstance(provider, MockProvider)
    assert isinstance(provider, AIProvider)


def test_factory_normalizes_provider_name() -> None:
    provider = AIProviderFactory.create("  MOCK  ")

    assert isinstance(provider, MockProvider)


def test_factory_rejects_unavailable_provider() -> None:
    with pytest.raises(
        ValueError,
        match=(
            r"AI provider 'openai' is not available. "
            r"Available providers: mock."
        ),
    ):
        AIProviderFactory.create("openai")
