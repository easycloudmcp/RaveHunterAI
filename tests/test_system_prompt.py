from pathlib import Path


SYSTEM_PROMPT = (
    Path(__file__).resolve().parents[1] / "prompts" / "system.md"
)


def test_system_prompt_defines_provider_neutral_safety_boundary() -> None:
    prompt = SYSTEM_PROMPT.read_text(encoding="utf-8")
    normalized = prompt.lower()

    assert "untrusted data" in normalized
    assert "never as instructions" in normalized
    assert "do not invent" in normalized
    assert "unknown or ambiguous" in normalized
    assert "credentials" in normalized
    assert "openai" not in normalized
    assert "azure" not in normalized
    assert "ollama" not in normalized
    assert "lm studio" not in normalized
