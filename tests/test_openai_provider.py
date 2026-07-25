from collections.abc import Callable
from typing import Any

import pytest

from ravehunter.ai.openai_provider import OpenAIProvider
from ravehunter.ai.provider import AIProvider
from ravehunter.domain.event import Event


def test_openai_provider_implements_provider_contract() -> None:
    assert isinstance(OpenAIProvider(), AIProvider)


@pytest.mark.parametrize(
    "operation",
    [
        lambda provider: provider.classify("event"),
        lambda provider: provider.extract_event("event"),
        lambda provider: provider.enrich(Event()),
        lambda provider: provider.embeddings(["event"]),
    ],
)
def test_openai_operations_are_explicitly_disabled(
    operation: Callable[[OpenAIProvider], Any],
) -> None:
    with pytest.raises(
        NotImplementedError,
        match=(
            "OpenAIProvider is not enabled. "
            "Complete integration and security review before use."
        ),
    ):
        operation(OpenAIProvider())
