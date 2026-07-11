from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_version_is_0252():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "0.25.2"


def test_release_notes_preserve_history_and_add_v0252():
    text = (
        ROOT / "docs" / "source" / "release_notes.rst"
    ).read_text(encoding="utf-8")
    assert text.startswith("Release notes\n=============\n\n")
    assert "v0.25.2 — Book 1 Companion v0.2.1 identity correction" in text
    assert "v0.25.1 — Chapter 20 power stability and release guard" in text
    assert "v0.25.0 — Book 1 Companion v0.2" in text
    assert "source-faithful, high-contrast grayscale figures" in text
    assert "v0.24.1 — Cross-platform Book 1 asset manifest" in text
    assert "v0.24.0 — Book 1 companion launcher" in text


def test_book1_launcher_docs_pin_current_route_and_preserve_v02_boundary():
    text = (
        ROOT / "docs" / "source" / "book1_launcher.rst"
    ).read_text(encoding="utf-8")
    assert 'pystatsv1[book1]==0.25.2' in text
    assert "psych_stats_with_python_companion_v0_2_1" in text
    assert 'pystatsv1[book1]==0.25.0' in text
    assert "psych_stats_with_python_companion_v0_2" in text
    normalized = " ".join(text.split())
    assert "synthetic teaching data only" in normalized
    assert "does not overwrite existing work" in normalized
    assert (
        "Chapter 10 correlation and Chapter 11 regression have separate "
        "source-faithful figures."
    ) in normalized


def test_root_readme_uses_current_book1_route_and_preserves_history():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 'pystatsv1[book1]==0.25.2' in text
    assert "psych_stats_with_python_companion_v0_2_1" in text
    assert "v0.25.0 with Companion v0.2" in text


def test_packaged_assets_configuration_includes_zip_assets():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_data = data["tool"]["setuptools"]["package-data"]
    assert "*.zip" in package_data["pystatsv1.assets"]


def test_ci_wheel_smoke_checks_historical_and_current_book1_assets():
    workflow = (
        ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")
    assert workflow.count("psych_stats_with_python_companion_v0_2.zip") >= 2
    assert workflow.count("psych_stats_with_python_companion_v0_2_1.zip") >= 2
    assert workflow.count("BOOK1_MAINTENANCE_RECEIPT.json") >= 2


def test_release_workflow_rehydrates_the_requested_annotated_version_tag():
    workflow = (
        ROOT / ".github" / "workflows" / "pypi-publish.yml"
    ).read_text(encoding="utf-8")
    checker = (
        ROOT / "tools" / "check_release_tag.py"
    ).read_text(encoding="utf-8")
    assert "release_tag:" in workflow
    assert "ref: ${{ inputs.release_tag }}" in workflow
    assert "fetch-depth: 0" in workflow
    assert "fetch-tags: true" in workflow
    assert '"refs/tags/${RELEASE_TAG}:refs/tags/${RELEASE_TAG}"' in workflow
    assert 'git cat-file -t "refs/tags/${RELEASE_TAG}"' in workflow
    assert "PYSTATSV1_RELEASE_ANNOTATED_TAG_FETCH_OK" in workflow
    assert "python tools/check_release_tag.py" in workflow
    assert "--exact-match" in checker
    assert "must be an annotated tag" in checker


def test_book1_historical_v02_asset_binding_remains_on_0250_proof_route():
    requirements = (
        ROOT
        / "book1_companion"
        / "psych_stats_with_python_companion_v0_2"
        / "requirements-book1-companion.txt"
    ).read_text(encoding="utf-8")
    assert "pystatsv1>=0.25.0,<0.26.0" in requirements


def test_book1_current_v021_asset_binding_targets_0252():
    root = (
        ROOT
        / "book1_companion"
        / "psych_stats_with_python_companion_v0_2_1"
    )
    requirements = (
        root / "requirements-book1-companion.txt"
    ).read_text(encoding="utf-8")
    provenance = (
        root / "BOOK1_SOURCE_PROVENANCE.json"
    ).read_text(encoding="utf-8")
    maintenance = (
        root / "BOOK1_MAINTENANCE_RECEIPT.json"
    ).read_text(encoding="utf-8")
    assert "pystatsv1>=0.25.2,<0.26.0" in requirements
    assert '"required_pystatsv1_release": "0.25.2"' in provenance
    assert '"package_version": "0.25.2"' in maintenance


def _load_release_checker():
    import importlib.util

    checker_path = ROOT / "tools" / "check_release_tag.py"
    spec = importlib.util.spec_from_file_location(
        "check_release_tag",
        checker_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_git(repo: Path, *args: str) -> None:
    import subprocess

    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _make_release_repo(repo: Path, *, version: str, tag: str) -> None:
    repo.mkdir()
    _run_git(repo, "init", "-q")
    _run_git(repo, "config", "user.email", "release-check@example.invalid")
    _run_git(repo, "config", "user.name", "Release Check")
    (repo / "pyproject.toml").write_text(
        "[project]\nname = \"fixture\"\nversion = \"" + version + "\"\n",
        encoding="utf-8",
    )
    _run_git(repo, "add", "pyproject.toml")
    _run_git(repo, "commit", "-qm", "fixture")
    _run_git(repo, "tag", "-a", tag, "-m", tag)


def test_release_tag_checker_accepts_exact_annotated_version_tag(tmp_path: Path):
    checker = _load_release_checker()
    repo = tmp_path / "matching"
    _make_release_repo(repo, version="0.25.1", tag="v0.25.1")
    assert checker.verify_release_tag(repo) == ("v0.25.1", "0.25.1")


def test_release_tag_checker_rejects_version_mismatch(tmp_path: Path):
    import pytest

    checker = _load_release_checker()
    repo = tmp_path / "mismatch"
    _make_release_repo(repo, version="0.25.1", tag="v0.25.0")
    with pytest.raises(checker.ReleaseCheckError, match="does not match"):
        checker.verify_release_tag(repo)

def test_book1_v021_design_audit_sources_builder_and_ci_route_are_declared():
    source = (
        ROOT
        / "book1_companion"
        / "psych_stats_with_python_companion_v0_2_1"
    )
    required = [
        "BOOK1_DESIGN_CONTRACT.json",
        "scripts/python/book1_design_contract.py",
        "scripts/python/audit_design_contract.py",
        "tests/test_book1_design_contract.py",
    ]
    for relative in required:
        assert (source / relative).is_file(), relative

    builder = (ROOT / "tools" / "build_book1_companion_asset.py").read_text(
        encoding="utf-8"
    )
    for relative in required:
        assert relative in builder
    assert '"--check-only"' in builder
    assert "BOOK1_COMPANION_DESIGN_AUDIT_OK" in builder

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert "make -C /tmp/book1_smoke design-audit" in workflow
    assert "make -C /tmp/book1-public design-audit" in workflow
    assert "scripts\\python\\audit_design_contract.py" in workflow
