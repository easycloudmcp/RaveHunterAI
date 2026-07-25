import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_distribution_includes_canonical_packages_and_prompts() -> None:
    configuration = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    setuptools = configuration["tool"]["setuptools"]

    assert "ravehunter*" in setuptools["packages"]["find"]["include"]
    assert setuptools["data-files"]["share/ravehunter/prompts"] == [
        "prompts/*.md"
    ]
    assert sorted(
        path.name for path in (PROJECT_ROOT / "prompts").glob("*.md")
    ) == [
        "classify_event.md",
        "extract_event.md",
        "system.md",
    ]
