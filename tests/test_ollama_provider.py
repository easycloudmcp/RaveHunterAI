from collections.abc import Callable
from typing import Any

import pytest

from ravehunter.ai.ollama_provider import OllamaProvider
from ravehunter.ai.provider import AIProvider
from ravehunter.domain.event import Event


def test_ollama_provider_implements_provider_contract() -> None:
    assert isinstance(OllamaProvider(), AIProvider)


@pytest.mark.parametrize(
    "operation",
    [
        lambda provider: provider.classify("event"),
        lambda provider: provider.extract_event("event"),
        lambda provider: provider.enrich(Event()),
        lambda provider: provider.embeddings(["event"]),
    ],
)
def test_ollama_operations_are_explicitly_disabled(
    operation: Callable[[OllamaProvider], Any],
) -> None:
    with pytest.raises(
        NotImplementedError,
        match=(
            "OllamaProvider is not enabled. "
            "Define local runtime limits and security policy before use."
        ),
    ):
        operation(OllamaProvider())
