from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "release_proofs" / "psych_design_v0_1"
EVIDENCE = PROOF / "evidence"
AUTHORIZATION = PROOF / "PYPI_RELEASE_AUTHORIZATION.json"
PUBLIC_RECEIPT = EVIDENCE / "PSYCH_DESIGN_PUBLIC_RELEASE.json"
READINESS = EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json"
ASSET = (
    ROOT
    / "src"
    / "pystatsv1"
    / "assets"
    / "psychological_statistics_by_design_companion_v0_1.zip"
)
CHECKER_PATH = ROOT / "tools" / "check_psych_design_public_release.py"
VERIFIER_PATH = ROOT / "tools" / "verify_pystatsv1_public_release.py"
EXPECTED_PATHS = [
    ".github/workflows/pypi-publish.yml",
    "Makefile",
    "README.md",
    "docs/PYSTATSV1_DROPIN_035_OWNER_AUTHORIZED_V0260_PUBLIC_RELEASE.md",
    "docs/source/release_notes.rst",
    "release_proofs/psych_design_v0_1/PYPI_RELEASE_AUTHORIZATION.json",
    "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_PUBLIC_RELEASE.json",
    "tests/test_psych_design_public_release.py",
    "tests/test_psych_design_release_proof.py",
    "tests/test_release_025_metadata.py",
    "tools/check_psych_design_public_release.py",
    "tools/check_psych_design_release_proof.py",
    "tools/verify_pystatsv1_public_release.py",
]

POST_TAG_REPAIR_PATHS = [
    ".github/workflows/ci.yml",
    ".github/workflows/dropin-035-v0260-tag-ci-repair.yml",
    ".github/workflows/pypi-publish.yml",
    "tests/test_psych_design_public_release.py",
    "tools/check_psych_design_public_release.py",
]
PUBLIC_RECEIPT_RELATIVE = (
    "release_proofs/psych_design_v0_1/evidence/"
    "PSYCH_DESIGN_PUBLIC_RELEASE.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checker():
    return load_module("public_release_checker_for_tests", CHECKER_PATH)


def verifier():
    return load_module("public_release_verifier_for_tests", VERIFIER_PATH)


def test_owner_authorization_is_exact_and_bounded() -> None:
    auth = load(AUTHORIZATION)
    assert auth["schema_version"] == (
        "pystatsv1-psych-design-pypi-release-authorization-v0.1"
    )
    assert auth["dropin"] == "035"
    assert auth["status"] == "owner_authorized_pending_publication"
    assert auth["authorization"]["status"] == "explicitly_authorized"
    assert auth["authorization_state"] == {
        "pypi_release_authorized": True,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
    }
    assert auth["release_identity"]["approved_parent_commit"] == (
        "400a3d688fb3c341fd393aca715de6d941b7f1e6"
    )
    assert auth["release_identity"]["release_tag"] == "v0.26.0"
    assert auth["release_identity"]["proof_tag"] == (
        "psych-design-companion-v0-1-release-proof"
    )
    assert auth["allowed_release_commit_paths"] == EXPECTED_PATHS


def test_authorization_protects_package_science_book_and_portal() -> None:
    boundaries = load(AUTHORIZATION)["protected_release_boundaries"]
    assert boundaries == {
        "analysis_or_dataset_changes_allowed": False,
        "book_or_portal_changes_allowed": False,
        "companion_asset_changes_allowed": False,
        "package_runtime_changes_allowed": False,
        "proof_contract_changes_allowed": False,
        "real_data_authorized": False,
    }
    assert not any(path.startswith("src/") for path in EXPECTED_PATHS)
    assert not any(path.startswith("psych_design_companion/") for path in EXPECTED_PATHS)


def test_dropin_034_readiness_remains_immutable_and_closed() -> None:
    state = load(READINESS)
    assert state["technical_release_ready"] is True
    assert state["clean_ubuntu_proof_passed"] is True
    assert state["clean_wsl_proof_passed"] is True
    assert state["cross_platform_comparison_passed"] is True
    assert state["pypi_release_authorized"] is False
    assert state["portal_release_authorized"] is False
    assert state["book_binding_authorized"] is False
    assert state["real_data_authorized"] is False


def test_public_receipt_lifecycle_preserves_exact_authorization_boundary() -> None:
    receipt = load(PUBLIC_RECEIPT)
    assert receipt["status"] in {
        "owner_authorized_pending_publication",
        "public_release_verified",
    }
    if receipt["status"] == "owner_authorized_pending_publication":
        assert receipt["public_artifacts_verified"] is False
        assert receipt["release_commit"] == "pending_until_v0.26.0_tag_creation"
    else:
        assert receipt["public_artifacts_verified"] is True
        assert len(receipt["release_commit"]) == 40
    assert receipt["authorization_state"] == {
        "pypi_release_authorized": True,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
    }


def test_governed_asset_identity_is_unchanged() -> None:
    import hashlib

    assert ASSET.stat().st_size == 136801
    assert hashlib.sha256(ASSET.read_bytes()).hexdigest() == (
        "bd0932c1d126758f37fab180173d6b95b5e4c31bc654724251aa6eb6296243c1"
    )


def test_release_notes_and_readme_expose_public_route_and_boundaries() -> None:
    notes = (ROOT / "docs/source/release_notes.rst").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "v0.26.0 — Psychological Statistics by Design companion v0.1" in notes
    assert "v0.26.0 release candidate" not in notes
    assert "trusted-publisher delivery" in notes
    assert 'pystatsv1[psych-design]==0.26.0' in readme
    assert "native Ubuntu and Windows 11 WSL2" in readme
    assert "synthetic-only" in readme
    assert "real-data use remain separately governed" in readme


def test_publish_workflow_is_manual_trusted_and_fully_gated() -> None:
    workflow = (ROOT / ".github/workflows/pypi-publish.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert 'if [ "$RELEASE_TAG" != "v0.26.0" ]' in workflow
    assert "python tools/check_release_tag.py" in workflow
    assert "python tools/check_psych_design_release_proof.py --phase complete" in workflow
    assert "python tools/check_psych_design_public_release.py --phase authorization" in workflow
    assert "python tools/build_psych_design_companion_asset.py" in workflow
    assert '"build>=1.2,<2"' in workflow
    assert "setuptools==80.9.0" in workflow
    assert "wheel==0.45.1" in workflow
    assert "numpy==2.2.6" in workflow
    assert "pandas==2.2.3" in workflow
    assert "PYSTATSV1_DROPIN_035_REPAIR3_BUILD_ENV_OK" in workflow
    assert "python -m build --no-isolation" in workflow
    assert "--phase distributions" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "psych-design-companion-v0-1-candidate" not in workflow


def test_publish_workflow_installs_audit_dependencies_before_asset_build() -> None:
    workflow = (ROOT / ".github/workflows/pypi-publish.yml").read_text(
        encoding="utf-8"
    )

    install_step = workflow.index(
        "Install deterministic build and companion-audit dependencies"
    )
    numpy_pin = workflow.index("numpy==2.2.6")
    pandas_pin = workflow.index("pandas==2.2.3")
    environment_marker = workflow.index(
        "PYSTATSV1_DROPIN_035_REPAIR3_BUILD_ENV_OK"
    )
    asset_build = workflow.index(
        "python tools/build_psych_design_companion_asset.py"
    )
    distribution_build = workflow.index("python -m build --no-isolation")
    publish_action = workflow.index("pypa/gh-action-pypi-publish@release/v1")

    assert install_step < numpy_pin < environment_marker < asset_build
    assert install_step < pandas_pin < environment_marker < asset_build
    assert asset_build < distribution_build < publish_action


def test_post_tag_scope_includes_only_bounded_publish_build_repair() -> None:
    module = checker()
    assert ".github/workflows/pypi-publish.yml" in module.POST_TAG_CI_REPAIR_PATHS
    assert sorted(module.POST_TAG_CI_REPAIR_PATHS) == POST_TAG_REPAIR_PATHS


def test_makefile_exposes_dropin_035_checks() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "psych-design-public-release-check:" in text
    assert "psych-design-public-release-distributions-check:" in text
    assert "psych-design-public-release-public-check:" in text


def test_public_release_source_checker_passes_without_git_metadata() -> None:
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, str(CHECKER_PATH), "--phase", "source"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PYSTATSV1_PUBLIC_RELEASE_CHECK_OK" in completed.stdout


def test_authorization_document_checker_accepts_frozen_receipt() -> None:
    module = checker()
    module.verify_authorization_document(load(AUTHORIZATION))


@pytest.mark.parametrize(
    "gate",
    ("portal_release_authorized", "book_binding_authorized", "real_data_authorized"),
)
def test_authorization_document_rejects_open_non_pypi_gate(gate: str) -> None:
    module = checker()
    auth = load(AUTHORIZATION)
    auth["authorization_state"][gate] = True
    with pytest.raises(module.PublicReleaseCheckError, match=gate):
        module.verify_authorization_document(auth)


def test_authorization_document_requires_pypi_authorization() -> None:
    module = checker()
    auth = load(AUTHORIZATION)
    auth["authorization_state"]["pypi_release_authorized"] = False
    with pytest.raises(module.PublicReleaseCheckError, match="not authorized"):
        module.verify_authorization_document(auth)


def test_technical_readiness_checker_accepts_completed_dropin_034() -> None:
    checker().verify_technical_readiness()


def _scope_git_stub(module, post_tag_paths: list[str]):
    release_commit = "a" * 40
    parent = load(AUTHORIZATION)["release_identity"]["approved_parent_commit"]

    def fake_git(*args: str, check: bool = True) -> str:
        del check
        if args == ("cat-file", "-e", f"{parent}^{{commit}}"):
            return ""
        if args == ("diff", "--name-only", "HEAD"):
            return ""
        if args == ("ls-files", "--others", "--exclude-standard"):
            return ""
        if args == ("tag", "--list"):
            return module.EXPECTED_RELEASE_TAG
        if args == (
            "cat-file",
            "-t",
            f"refs/tags/{module.EXPECTED_RELEASE_TAG}",
        ):
            return "tag"
        if args == (
            "rev-parse",
            f"{module.EXPECTED_RELEASE_TAG}^{{commit}}",
        ):
            return release_commit
        if args == ("diff", "--name-only", f"{parent}..{release_commit}"):
            return "\n".join(EXPECTED_PATHS)
        if args == ("diff", "--name-only", f"{release_commit}..HEAD"):
            return "\n".join(post_tag_paths)
        raise AssertionError(f"unexpected git call: {args}")

    return fake_git


def _patch_release_scope_git(
    module,
    monkeypatch: pytest.MonkeyPatch,
    post_tag_paths: list[str],
    receipt_status: str,
) -> None:
    receipt = load(PUBLIC_RECEIPT)
    receipt["status"] = receipt_status
    monkeypatch.setattr(module, "_has_git", lambda: True)
    monkeypatch.setattr(module, "_git", _scope_git_stub(module, post_tag_paths))
    monkeypatch.setattr(module, "load", lambda _path: receipt)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0),
    )


def test_pending_post_tag_path_policy_is_exact_and_bounded() -> None:
    module = checker()
    receipt = load(PUBLIC_RECEIPT)
    receipt["status"] = "owner_authorized_pending_publication"
    assert module.expected_post_tag_paths(receipt) == POST_TAG_REPAIR_PATHS


def test_verified_post_tag_path_policy_adds_only_public_receipt() -> None:
    module = checker()
    receipt = load(PUBLIC_RECEIPT)
    receipt["status"] = "public_release_verified"
    assert module.expected_post_tag_paths(receipt) == sorted(
        POST_TAG_REPAIR_PATHS + [PUBLIC_RECEIPT_RELATIVE]
    )


def test_release_source_scope_accepts_exact_pending_post_tag_repairs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    _patch_release_scope_git(
        module,
        monkeypatch,
        POST_TAG_REPAIR_PATHS,
        "owner_authorized_pending_publication",
    )
    module.verify_release_source_paths(load(AUTHORIZATION))


def test_release_source_scope_rejects_extra_post_tag_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    _patch_release_scope_git(
        module,
        monkeypatch,
        POST_TAG_REPAIR_PATHS + ["src/pystatsv1/cli.py"],
        "owner_authorized_pending_publication",
    )
    with pytest.raises(
        module.PublicReleaseCheckError,
        match="post-tag path scope differs",
    ):
        module.verify_release_source_paths(load(AUTHORIZATION))


def test_release_source_scope_rejects_missing_governed_repair_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    _patch_release_scope_git(
        module,
        monkeypatch,
        POST_TAG_REPAIR_PATHS[:-1],
        "owner_authorized_pending_publication",
    )
    with pytest.raises(
        module.PublicReleaseCheckError,
        match="post-tag path scope differs",
    ):
        module.verify_release_source_paths(load(AUTHORIZATION))


def test_release_source_scope_accepts_verified_public_receipt_delta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    _patch_release_scope_git(
        module,
        monkeypatch,
        POST_TAG_REPAIR_PATHS + [PUBLIC_RECEIPT_RELATIVE],
        "public_release_verified",
    )
    module.verify_release_source_paths(load(AUTHORIZATION))


def test_release_source_scope_rejects_public_receipt_before_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    _patch_release_scope_git(
        module,
        monkeypatch,
        POST_TAG_REPAIR_PATHS + [PUBLIC_RECEIPT_RELATIVE],
        "owner_authorized_pending_publication",
    )
    with pytest.raises(
        module.PublicReleaseCheckError,
        match="post-tag path scope differs",
    ):
        module.verify_release_source_paths(load(AUTHORIZATION))


def _write_wheel(path: Path, module, *, asset: bytes | None = None, version: str = "0.26.0") -> None:
    asset = ASSET.read_bytes() if asset is None else asset
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"pystatsv1-{version}.dist-info/METADATA",
            f"Metadata-Version: 2.4\nName: pystatsv1\nVersion: {version}\n\n",
        )
        archive.writestr(module.ASSET_MEMBER, asset)
        archive.writestr(f"pystatsv1-{version}.dist-info/RECORD", "")


def _add_tar_bytes(archive: tarfile.TarFile, name: str, payload: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def _write_sdist(path: Path, module, *, asset: bytes | None = None, version: str = "0.26.0") -> None:
    asset = ASSET.read_bytes() if asset is None else asset
    root = f"pystatsv1-{version}"
    with tarfile.open(path, "w:gz") as archive:
        _add_tar_bytes(
            archive,
            f"{root}/PKG-INFO",
            f"Metadata-Version: 2.4\nName: pystatsv1\nVersion: {version}\n\n".encode(),
        )
        _add_tar_bytes(archive, f"{root}/pyproject.toml", b"[project]\n")
        _add_tar_bytes(archive, f"{root}/{module.SDIST_ASSET_SUFFIX}", asset)


def test_wheel_inspector_accepts_exact_public_identity(tmp_path: Path) -> None:
    module = verifier()
    wheel = tmp_path / module.EXPECTED_WHEEL
    _write_wheel(wheel, module)
    result = module.inspect_wheel(wheel)
    assert result["metadata_name"] == "pystatsv1"
    assert result["metadata_version"] == "0.26.0"
    assert result["embedded_asset_sha256"] == module.ASSET_SHA256
    assert result["embedded_asset_bytes"] == 136801


def test_wheel_inspector_rejects_changed_asset(tmp_path: Path) -> None:
    module = verifier()
    wheel = tmp_path / module.EXPECTED_WHEEL
    payload = bytearray(ASSET.read_bytes())
    payload[0] ^= 1
    _write_wheel(wheel, module, asset=bytes(payload))
    with pytest.raises(module.PublicReleaseError, match="asset hash changed"):
        module.inspect_wheel(wheel)


def test_wheel_inspector_rejects_changed_metadata_version(tmp_path: Path) -> None:
    module = verifier()
    wheel = tmp_path / module.EXPECTED_WHEEL
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "pystatsv1-0.26.0.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: pystatsv1\nVersion: 0.25.2\n\n",
        )
        archive.writestr(module.ASSET_MEMBER, ASSET.read_bytes())
        archive.writestr("pystatsv1-0.26.0.dist-info/RECORD", "")
    with pytest.raises(module.PublicReleaseError, match="version is not 0.26.0"):
        module.inspect_wheel(wheel)


def test_sdist_inspector_accepts_exact_public_identity(tmp_path: Path) -> None:
    module = verifier()
    sdist = tmp_path / module.EXPECTED_SDIST
    _write_sdist(sdist, module)
    result = module.inspect_sdist(sdist)
    assert result["metadata_name"] == "pystatsv1"
    assert result["metadata_version"] == "0.26.0"
    assert result["embedded_asset_sha256"] == module.ASSET_SHA256


def test_sdist_inspector_rejects_changed_asset(tmp_path: Path) -> None:
    module = verifier()
    sdist = tmp_path / module.EXPECTED_SDIST
    payload = bytearray(ASSET.read_bytes())
    payload[-1] ^= 1
    _write_sdist(sdist, module, asset=bytes(payload))
    with pytest.raises(module.PublicReleaseError, match="asset identity changed"):
        module.inspect_sdist(sdist)


def test_sdist_inspector_rejects_links(tmp_path: Path) -> None:
    module = verifier()
    sdist = tmp_path / module.EXPECTED_SDIST
    with tarfile.open(sdist, "w:gz") as archive:
        info = tarfile.TarInfo("pystatsv1-0.26.0/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "../../unsafe"
        archive.addfile(info)
    with pytest.raises(module.PublicReleaseError, match="link member"):
        module.inspect_sdist(sdist)


def test_distribution_directory_requires_exact_wheel_and_sdist(tmp_path: Path) -> None:
    module = verifier()
    _write_wheel(tmp_path / module.EXPECTED_WHEEL, module)
    _write_sdist(tmp_path / module.EXPECTED_SDIST, module)
    result = module.inspect_distribution_directory(tmp_path)
    assert result["embedded_asset_identity_exact"] is True
    (tmp_path / "unexpected.txt").write_text("x", encoding="utf-8")
    with pytest.raises(module.PublicReleaseError, match="exactly"):
        module.inspect_distribution_directory(tmp_path)


def _smoke() -> dict:
    return {
        "status": "pass",
        "command_status": {
            "pip_install_public_exact": True,
            "psych_design_info": True,
            "psych_design_init": True,
            "verify_before": True,
            "doctor": True,
            "first_result": True,
            "verify_after": True,
        },
    }


def _distributions(module) -> dict:
    row = {
        "filename": module.EXPECTED_WHEEL,
        "sha256": "a" * 64,
        "embedded_asset_sha256": module.ASSET_SHA256,
    }
    sdist = {
        "filename": module.EXPECTED_SDIST,
        "sha256": "b" * 64,
        "embedded_asset_sha256": module.ASSET_SHA256,
    }
    return {"wheel": row, "sdist": sdist, "embedded_asset_identity_exact": True}


def test_public_receipt_builder_accepts_verified_release() -> None:
    module = verifier()
    receipt = module.build_public_receipt(
        release_commit="c" * 40,
        tag_ci_run_id="123",
        publish_workflow_run_id="456",
        distributions=_distributions(module),
        smoke=_smoke(),
    )
    assert receipt["status"] == "public_release_verified"
    assert receipt["public_artifacts_verified"] is True
    assert receipt["authorization_state"] == {
        "pypi_release_authorized": True,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
    }


def test_public_receipt_builder_rejects_invalid_release_commit() -> None:
    module = verifier()
    with pytest.raises(module.PublicReleaseError, match="40-character"):
        module.build_public_receipt(
            release_commit="short",
            tag_ci_run_id="123",
            publish_workflow_run_id="456",
            distributions=_distributions(module),
            smoke=_smoke(),
        )


def test_public_receipt_builder_rejects_failed_command() -> None:
    module = verifier()
    smoke = _smoke()
    smoke["command_status"]["first_result"] = False
    with pytest.raises(module.PublicReleaseError, match="every command"):
        module.build_public_receipt(
            release_commit="c" * 40,
            tag_ci_run_id="123",
            publish_workflow_run_id="456",
            distributions=_distributions(module),
            smoke=smoke,
        )


def test_public_phase_rejects_pending_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    pending = {
        "schema_version": "pystatsv1-psych-design-public-release-v0.1",
        "status": "owner_authorized_pending_publication",
        "package_version": "0.26.0",
        "public_artifacts_verified": False,
        "authorization_state": {
            "pypi_release_authorized": True,
            "portal_release_authorized": False,
            "book_binding_authorized": False,
            "real_data_authorized": False,
        },
    }
    monkeypatch.setattr(module, "load", lambda _path: pending)
    with pytest.raises(module.PublicReleaseCheckError, match="has not been verified"):
        module.verify_public_receipt(load(AUTHORIZATION))


def test_public_receipt_checker_rejects_open_non_pypi_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = checker()
    receipt = {
        "schema_version": "pystatsv1-psych-design-public-release-v0.1",
        "package_version": "0.26.0",
        "status": "public_release_verified",
        "public_artifacts_verified": True,
        "trusted_publisher": True,
        "scientific_candidate_unchanged": True,
        "release_commit": "c" * 40,
        "tag_ci_run_id": "123",
        "publish_workflow_run_id": "456",
        "artifacts": _distributions(verifier()),
        "reader_smoke": {
            "status": "pass",
            "installed_version": "0.26.0",
            "installed_asset_sha256": module.EXPECTED_ASSET_SHA256,
            "command_status": {"x": True},
            "first_result_outputs": {"x": True},
            "absolute_workspace_path_recorded": False,
        },
        "authorization_state": {
            "pypi_release_authorized": True,
            "portal_release_authorized": True,
            "book_binding_authorized": False,
            "real_data_authorized": False,
        },
    }
    monkeypatch.setattr(module, "load", lambda _path: receipt)
    monkeypatch.setattr(module, "verify_release_tag", lambda *_args, **_kwargs: "c" * 40)
    with pytest.raises(module.PublicReleaseCheckError, match="opens closed gate"):
        module.verify_pending_public_receipt()


def test_dropin_035_tag_ci_repair_workflow_preserves_immutable_annotated_tag() -> None:
    workflow = (
        ROOT / ".github/workflows/dropin-035-v0260-tag-ci-repair.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert 'default: "v0.26.0"' in workflow
    assert "windows-py310-tag-repair:" in workflow
    assert "ref: ${{ inputs.release_tag }}" in workflow
    assert "fetch-depth: 0" in workflow
    assert "fetch-tags: true" in workflow
    assert (
        'git fetch --force origin "refs/tags/$($env:RELEASE_TAG):refs/tags/$($env:RELEASE_TAG)"'
        in workflow
    )
    assert 'git cat-file -t "refs/tags/$($env:RELEASE_TAG)"' in workflow
    assert 'git rev-parse "refs/tags/$($env:RELEASE_TAG)^{commit}"' in workflow
    assert "git rev-parse HEAD" in workflow
    assert "PYSTATSV1_DROPIN_035_REPAIR1_ANNOTATED_TAG_OK" in workflow
    assert "make lint" in workflow
    assert "make docs" in workflow
    assert "make test" in workflow
    assert "make ch13-ci" in workflow
    assert "gh-action-pypi-publish" not in workflow
    assert "git tag -f" not in workflow
    assert "git push --force" not in workflow


def test_windows_ci_restores_annotated_v0260_tag_before_full_tests() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    windows_job = workflow.split("  windows-py310:", maxsplit=1)[1]
    restore = windows_job.split("      - name: Set up Python", maxsplit=1)[0]

    assert "Restore annotated v0.26.0 tag when present" in restore
    assert 'git ls-remote --tags origin "refs/tags/v0.26.0"' in restore
    assert (
        'git fetch --force origin "refs/tags/v0.26.0:refs/tags/v0.26.0"'
        in restore
    )
    assert 'git cat-file -t "refs/tags/v0.26.0"' in restore
    assert 'if ($objectType -ne "tag")' in restore
    assert "PYSTATSV1_WINDOWS_CI_ANNOTATED_TAG_OK" in restore
