from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_version_is_0250():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "0.25.0"


def test_release_notes_preserve_history_and_add_v0250():
    text = (ROOT / "docs" / "source" / "release_notes.rst").read_text(encoding="utf-8")
    assert text.startswith("Release notes\n=============\n\n")
    assert "v0.25.0 — Book 1 Companion v0.2" in text
    assert "source-faithful, high-contrast grayscale figures" in text
    assert "v0.24.1 — Cross-platform Book 1 asset manifest" in text
    assert "v0.24.0 — Book 1 companion launcher" in text


def test_book1_launcher_docs_pin_the_matching_release_and_v02_boundary():
    text = (ROOT / "docs" / "source" / "book1_launcher.rst").read_text(encoding="utf-8")
    assert 'pystatsv1[book1]==0.25.0' in text
    assert "psych_stats_with_python_companion_v0_2" in text
    normalized = " ".join(text.split())
    assert "synthetic teaching data only" in normalized
    assert "does not overwrite existing work" in normalized
    assert "Chapter 10 correlation and Chapter 11 regression have separate source-faithful figures." in normalized


def test_packaged_assets_configuration_includes_zip_assets():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_data = data["tool"]["setuptools"]["package-data"]
    assert "*.zip" in package_data["pystatsv1.assets"]
