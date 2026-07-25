from ravehunter.ai import (
    AIProvider,
    AIProviderFactory,
    ClassificationResult,
    MockProvider,
)


def test_ai_package_exposes_stable_public_api() -> None:
    provider = AIProviderFactory.create()

    assert isinstance(provider, AIProvider)
    assert isinstance(provider, MockProvider)
    assert ClassificationResult(
        label="event",
        confidence=1.0,
    ).label == "event"
