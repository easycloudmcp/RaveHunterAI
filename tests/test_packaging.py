import os
import subprocess
import sys
import tomllib
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_distribution_includes_canonical_packages_and_prompts() -> None:
    configuration = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    setuptools = configuration["tool"]["setuptools"]

    assert "ravehunter*" in setuptools["packages"]["find"]["include"]
    assert setuptools["data-files"]["share/ravehunter/prompts"] == ["prompts/*.md"]
    assert sorted(path.name for path in (PROJECT_ROOT / "prompts").glob("*.md")) == [
        "classify_event.md",
        "extract_event.md",
        "system.md",
    ]


def test_installed_wheel_exposes_unified_cli(tmp_path: Path) -> None:
    configuration = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert configuration["project"]["scripts"]["ravehunter"] == "ravehunter.cli:main"

    distribution = tmp_path / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(distribution),
            ".",
        ],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(distribution.glob("*.whl"))
    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=True).create(environment)
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    command = scripts / ("ravehunter.exe" if os.name == "nt" else "ravehunter")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )

    run_directory = tmp_path / "outside-repository"
    run_directory.mkdir()
    cli_environment = {
        **os.environ,
        "RAVEHUNTER_DATABASE": str(tmp_path / "events.db"),
    }
    for arguments in (
        ["--help"],
        ["collect", "meta", "--help"],
        ["collect", "shotgun", "--help"],
        ["events", "list", "--help"],
        ["events", "show", "--help"],
    ):
        result = subprocess.run(
            [str(command), *arguments],
            cwd=run_directory,
            env=cli_environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    missing = subprocess.run(
        [str(command), "events", "show", "missing-id"],
        cwd=run_directory,
        env=cli_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode == 1
    assert missing.stdout.strip() == "Event not found."

    imported = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import pathlib, ravehunter.cli; print(pathlib.Path("
                "ravehunter.cli.__file__).resolve())"
            ),
        ],
        cwd=run_directory,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(PROJECT_ROOT) not in imported.stdout
