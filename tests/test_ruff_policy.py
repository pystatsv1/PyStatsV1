from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUFF_VERSION = "0.16.0"


def test_ruff_version_is_pinned_in_both_dependency_surfaces() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    assert f'"ruff=={RUFF_VERSION}"' in pyproject
    assert f"ruff=={RUFF_VERSION}" in requirements.splitlines()


def test_ruff_policy_is_explicit_and_stable() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "[tool.ruff]" in pyproject
    assert f'required-version = "=={RUFF_VERSION}"' in pyproject
    assert 'target-version = "py310"' in pyproject
    assert "[tool.ruff.lint]" in pyproject
    assert 'select = ["E4", "E7", "E9", "F"]' in pyproject


def test_windows_ci_reports_the_governed_ruff_version() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "ruff --version" in workflow
    assert "make lint" in workflow
