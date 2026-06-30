from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
HELPERS = [
    "package_identity()",
    "describe_by_group()",
    "write_json_receipt()",
    "compare_numeric_results()",
]


def test_release_notes_document_psych_helpers():
    text = (ROOT / "docs" / "source" / "release_notes.rst").read_text(encoding="utf-8")
    assert "v0.23.0" in text
    assert "APA Lab support helpers" in text
    for helper in HELPERS:
        assert helper in text


def test_psych_support_helper_docs_include_install_and_claim_boundary():
    text = (ROOT / "docs" / "source" / "psych_support_helpers.rst").read_text(encoding="utf-8")
    assert 'pystatsv1==0.23.0' in text
    assert "Python for the workflow" in text
    assert "R for verification" in text
    assert "PyStatsV1 for the bridge" in text
    assert "do not replace SciPy, statsmodels" in text
    for helper in HELPERS:
        assert helper in text


def test_docs_index_links_release_notes_and_psych_helpers():
    text = (ROOT / "docs" / "source" / "index.rst").read_text(encoding="utf-8")
    assert "release_notes" in text
    assert "psych_support_helpers" in text


def test_ci_runs_on_release_tags_before_publish():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "tags:" in text
    assert '"v*"' in text or "'v*'" in text


def test_pypi_publish_is_manual_after_green_tag_ci():
    text = (ROOT / ".github" / "workflows" / "pypi-publish.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "push:" not in text
    assert "gh workflow run pypi-publish.yml --ref v0.23.0" in text


def test_dev_extra_supports_py310_release_build():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev = data["project"]["optional-dependencies"]["dev"]
    assert any(dep.startswith("build>=") for dep in dev)
    assert any(dep.startswith("tomli>=") and "python_version < '3.11'" in dep for dep in dev)
