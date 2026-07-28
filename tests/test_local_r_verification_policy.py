from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow_text() -> str:
    paths = [*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")]
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(paths)
    )


def test_no_github_workflow_installs_or_executes_r() -> None:
    text = workflow_text()
    prohibited = (
        "apt-get install --yes r-base",
        "r-cran-nlme",
        "Rscript",
        "psych-design-swl-s02-s05-r-verify",
        "psych-design-swl-s01-s06-s07-r-verify",
        "psych-design-swl-s08-s10-r-verify",
    )
    for token in prohibited:
        assert token not in text


def test_retired_dedicated_r_workflows_are_absent() -> None:
    retired = (
        "psych-design-swl-first-batch-r-verify.yml",
        "psych-design-swl-second-batch-r-verify.yml",
        "psych-design-swl-final-batch-r-verify.yml",
    )
    for filename in retired:
        assert not (WORKFLOWS / filename).exists()


def test_book1_github_smoke_is_python_only() -> None:
    text = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "book1-companion-release-smoke:" in text
    assert "Build wheel and run Python-only Book 1 smoke" in text
    assert "make -C /tmp/book1-public python-only" in text
    assert "make -C /tmp/book1-public figures" in text
    assert "make -C /tmp/book1-public all" not in text
    assert "Install R for public companion parity smoke" not in text


def test_local_runner_covers_all_required_r_surfaces() -> None:
    text = (ROOT / "tools" / "run_local_r_verification.py").read_text(encoding="utf-8")
    required = (
        "psych-design-swl-s02-s05-r-verify",
        "psych-design-swl-s01-s06-s07-environment-verify",
        "psych-design-swl-s01-s06-s07-r-verify",
        "psych-design-swl-s08-s10-r-verify",
        '"r-check"',
        '"parity"',
        "PYSTATSV1_LOCAL_R_VERIFICATION_OK",
        "LOCAL_R_VERIFICATION_RECEIPT.json",
    )
    for token in required:
        assert token in text


def test_local_runner_requires_r_and_nlme() -> None:
    text = (ROOT / "tools" / "run_local_r_verification.py").read_text(encoding="utf-8")
    assert 'shutil.which("Rscript")' in text
    assert "requireNamespace('nlme'" in text


def test_makefile_exposes_single_local_r_gate() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: local-r-verify" in text
    assert "local-r-verify:" in text
    assert 'tools/run_local_r_verification.py --python "$(PYTHON)"' in text


def test_policy_documents_cost_and_evidence_boundary() -> None:
    text = (ROOT / "docs" / "LOCAL_R_VERIFICATION_POLICY.md").read_text(encoding="utf-8")
    assert "GitHub-hosted Actions no longer install or execute R" in text
    assert "local-r-verify" in text
    assert "build/local_r_verification/LOCAL_R_VERIFICATION_RECEIPT.json" in text
    assert "does not claim Python/R parity" in text


def test_local_runner_preserves_virtualenv_python_symlink(tmp_path: Path) -> None:
    from tools.run_local_r_verification import normalize_python_executable

    venv_bin = tmp_path / "governed-venv" / "bin"
    venv_bin.mkdir(parents=True)
    venv_python = venv_bin / "python"
    venv_python.symlink_to(Path(sys.executable))

    normalized = normalize_python_executable(str(venv_python))

    assert normalized == str(venv_python.absolute())
    assert Path(normalized).is_symlink()
    assert Path(normalized).resolve() == Path(sys.executable).resolve()


def test_local_runner_does_not_resolve_governed_python_path() -> None:
    text = (ROOT / "tools" / "run_local_r_verification.py").read_text(
        encoding="utf-8"
    )
    assert "normalize_python_executable" in text
    assert "os.path.abspath" in text
    assert "Path(args.python).expanduser().resolve()" not in text
