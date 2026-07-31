#!/usr/bin/env python3
"""Verify Drop-in 035 PyPI authorization, distributions, and public receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "release_proofs" / "psych_design_v0_1"
EVIDENCE = PROOF / "evidence"
AUTHORIZATION = PROOF / "PYPI_RELEASE_AUTHORIZATION.json"
READINESS = EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json"
PUBLIC_RECEIPT = EVIDENCE / "PSYCH_DESIGN_PUBLIC_RELEASE.json"
ASSET = (
    ROOT
    / "src"
    / "pystatsv1"
    / "assets"
    / "psychological_statistics_by_design_companion_v0_1.zip"
)
PYPROJECT = ROOT / "pyproject.toml"
WORKFLOW = ROOT / ".github" / "workflows" / "pypi-publish.yml"
RELEASE_NOTES = ROOT / "docs" / "source" / "release_notes.rst"
VERIFIER = ROOT / "tools" / "verify_pystatsv1_public_release.py"
EXPECTED_PARENT = "400a3d688fb3c341fd393aca715de6d941b7f1e6"
EXPECTED_PROOF_TAG = "psych-design-companion-v0-1-release-proof"
EXPECTED_RELEASE_TAG = "v0.26.0"
EXPECTED_VERSION = "0.26.0"
EXPECTED_ASSET_SHA256 = (
    "bd0932c1d126758f37fab180173d6b95b5e4c31bc654724251aa6eb6296243c1"
)
EXPECTED_ASSET_BYTES = 136801
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]
CLOSED_GATES = (
    "portal_release_authorized",
    "book_binding_authorized",
    "real_data_authorized",
)
POST_TAG_CI_REPAIR_PATHS = (
    ".github/workflows/ci.yml",
    ".github/workflows/dropin-035-v0260-tag-ci-repair.yml",
    "tests/test_psych_design_public_release.py",
    "tools/check_psych_design_public_release.py",
)
PUBLIC_RECEIPT_RELATIVE = (
    "release_proofs/psych_design_v0_1/evidence/"
    "PSYCH_DESIGN_PUBLIC_RELEASE.json"
)


class PublicReleaseCheckError(RuntimeError):
    """Raised when a Drop-in 035 release gate fails."""


def fail(message: str) -> None:
    raise PublicReleaseCheckError(message)


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        fail(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def _has_git() -> bool:
    return (ROOT / ".git").exists()


def project_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        fail("could not read project version")
    return match.group(1)


def load_verifier_module():
    spec = importlib.util.spec_from_file_location(
        "pystatsv1_public_release_verifier_for_checker", VERIFIER
    )
    if spec is None or spec.loader is None:
        fail("could not load public-release verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_authorization_document(auth: dict[str, Any]) -> None:
    if auth.get("schema_version") != (
        "pystatsv1-psych-design-pypi-release-authorization-v0.1"
    ):
        fail("authorization schema changed")
    if auth.get("dropin") != "035":
        fail("authorization is not Drop-in 035")
    if auth.get("status") != "owner_authorized_pending_publication":
        fail("authorization status changed")
    release = auth.get("release_identity", {})
    expected = {
        "approved_parent_commit": EXPECTED_PARENT,
        "candidate_commit": "58d92f85b865cb657bf49c731fefc381970c8bda",
        "candidate_tag": "psych-design-companion-v0-1-candidate",
        "package_name": "pystatsv1",
        "package_version": EXPECTED_VERSION,
        "proof_tag": EXPECTED_PROOF_TAG,
        "release_tag": EXPECTED_RELEASE_TAG,
    }
    for key, value in expected.items():
        if release.get(key) != value:
            fail(f"authorization release identity changed: {key}")
    authorization = auth.get("authorization", {})
    if authorization.get("status") != "explicitly_authorized":
        fail("repository-owner authorization is not explicit")
    state = auth.get("authorization_state", {})
    if state.get("pypi_release_authorized") is not True:
        fail("PyPI release is not authorized")
    for gate in CLOSED_GATES:
        if state.get(gate) is not False:
            fail(f"authorization opens closed gate: {gate}")
    boundaries = auth.get("protected_release_boundaries", {})
    for key in (
        "analysis_or_dataset_changes_allowed",
        "book_or_portal_changes_allowed",
        "companion_asset_changes_allowed",
        "package_runtime_changes_allowed",
        "proof_contract_changes_allowed",
        "real_data_authorized",
    ):
        if boundaries.get(key) is not False:
            fail(f"authorization weakens protected boundary: {key}")
    companion = auth.get("companion_identity", {})
    if companion.get("asset_sha256") != EXPECTED_ASSET_SHA256:
        fail("authorization asset hash changed")
    if companion.get("asset_bytes") != EXPECTED_ASSET_BYTES:
        fail("authorization asset byte size changed")
    if companion.get("immutable_source_file_count") != 151:
        fail("authorization source-file count changed")
    public = auth.get("public_artifact_policy", {})
    if public.get("trusted_publisher_required") is not True:
        fail("trusted publisher is no longer required")
    if public.get("fresh_public_install_required") is not True:
        fail("fresh public install is no longer required")


def verify_technical_readiness() -> None:
    readiness = load(READINESS)
    expected = {
        "candidate_implementation_passed": True,
        "clean_ubuntu_proof_passed": True,
        "clean_wsl_proof_passed": True,
        "cross_platform_comparison_passed": True,
        "technical_release_ready": True,
        "pypi_release_authorized": False,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
    }
    for key, value in expected.items():
        if readiness.get(key) is not value:
            fail(f"Drop-in 034 readiness changed: {key}")
    if readiness.get("status") != "technical_release_ready_not_authorized":
        fail("Drop-in 034 readiness status changed")
    if readiness.get("package_version") != EXPECTED_VERSION:
        fail("Drop-in 034 package version changed")


def verify_frozen_asset() -> None:
    if not ASSET.is_file():
        fail("governed companion asset is missing")
    if ASSET.stat().st_size != EXPECTED_ASSET_BYTES:
        fail("governed companion asset size changed")
    if sha256(ASSET) != EXPECTED_ASSET_SHA256:
        fail("governed companion asset hash changed")


def expected_post_tag_paths(receipt: dict[str, Any]) -> list[str]:
    status = receipt.get("status")
    paths = set(POST_TAG_CI_REPAIR_PATHS)
    if status == "public_release_verified":
        paths.add(PUBLIC_RECEIPT_RELATIVE)
    elif status != "owner_authorized_pending_publication":
        fail("public-release receipt has an invalid lifecycle status")
    return sorted(paths)


def verify_release_source_paths(auth: dict[str, Any]) -> None:
    expected = sorted(auth.get("allowed_release_commit_paths", []))
    if len(expected) != len(set(expected)) or len(expected) != 13:
        fail("authorized path list is invalid")
    if not _has_git():
        return

    parent = auth["release_identity"]["approved_parent_commit"]
    _git("cat-file", "-e", f"{parent}^{{commit}}")
    working = _git("diff", "--name-only", "HEAD").splitlines()
    untracked = _git("ls-files", "--others", "--exclude-standard").splitlines()
    tags = set(_git("tag", "--list").splitlines())

    if EXPECTED_RELEASE_TAG not in tags:
        committed = _git("diff", "--name-only", f"{parent}..HEAD").splitlines()
        actual = sorted(set(committed + working + untracked))
        if actual != expected:
            fail(
                "release-source path scope differs from authorization; "
                f"expected={expected}, actual={actual}"
            )
    else:
        if _git("cat-file", "-t", f"refs/tags/{EXPECTED_RELEASE_TAG}") != "tag":
            fail("v0.26.0 must be an annotated tag")
        release_commit = _git("rev-parse", f"{EXPECTED_RELEASE_TAG}^{{commit}}")
        tagged_paths = sorted(
            path
            for path in _git(
                "diff", "--name-only", f"{parent}..{release_commit}"
            ).splitlines()
            if path
        )
        if tagged_paths != expected:
            fail("v0.26.0 does not resolve to the authorized source diff")
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "merge-base",
                "--is-ancestor",
                release_commit,
                "HEAD",
            ],
            check=False,
        )
        if completed.returncode != 0:
            fail("v0.26.0 release commit is not an ancestor of HEAD")

        committed_after_tag = _git(
            "diff", "--name-only", f"{release_commit}..HEAD"
        ).splitlines()
        actual_post_tag = sorted(
            set(committed_after_tag + working + untracked)
        )
        expected_post_tag = expected_post_tag_paths(load(PUBLIC_RECEIPT))
        if actual_post_tag != expected_post_tag:
            fail(
                "post-tag path scope differs from governed repair lifecycle; "
                f"expected={expected_post_tag}, actual={actual_post_tag}"
            )
        actual = sorted(set(tagged_paths + actual_post_tag))

    forbidden_prefixes = (
        "src/",
        "psych_design_companion/",
        "data/",
        "book1_companion/",
        "release_proofs/psych_design_v0_1/RELEASE_PROOF_CONTRACT.json",
        "release_proofs/psych_design_v0_1/CANDIDATE_FREEZE.json",
        "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json",
        "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_WSL_RELEASE_PROOF.json",
        "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_CROSS_PLATFORM_COMPARISON.json",
        "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_WHEEL_IDENTITY.json",
        "release_proofs/psych_design_v0_1/evidence/PSYCH_DESIGN_ASSET_IDENTITY.json",
    )
    for path in actual:
        if path.startswith(forbidden_prefixes):
            fail(f"release source changes protected path: {path}")


def verify_proof_tag() -> None:
    if not _has_git():
        return
    tags = set(_git("tag", "--list").splitlines())
    if EXPECTED_PROOF_TAG not in tags:
        fail("release-proof tag is missing")
    proof_commit = _git("rev-parse", f"{EXPECTED_PROOF_TAG}^{{commit}}")
    if proof_commit != EXPECTED_PARENT:
        fail("release-proof tag moved")


def verify_release_tag(auth: dict[str, Any], *, required: bool) -> str | None:
    if not _has_git():
        return None
    tags = set(_git("tag", "--list").splitlines())
    if EXPECTED_RELEASE_TAG not in tags:
        if required:
            fail("v0.26.0 release tag is missing")
        return None
    if _git("cat-file", "-t", f"refs/tags/{EXPECTED_RELEASE_TAG}") != "tag":
        fail("v0.26.0 must be an annotated tag")
    commit = _git("rev-parse", f"{EXPECTED_RELEASE_TAG}^{{commit}}")
    parent = auth["release_identity"]["approved_parent_commit"]
    tagged_paths = sorted(
        path
        for path in _git("diff", "--name-only", f"{parent}..{commit}").splitlines()
        if path
    )
    expected = sorted(auth["allowed_release_commit_paths"])
    if tagged_paths != expected:
        fail("v0.26.0 does not resolve to the authorized source diff")
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
    )
    if completed.returncode != 0:
        fail("v0.26.0 release commit is not an ancestor of HEAD")
    return commit


def verify_publication_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = (
        "workflow_dispatch:",
        "environment: pypi",
        "id-token: write",
        "python tools/check_release_tag.py",
        "python tools/check_psych_design_release_proof.py --phase complete",
        "python tools/check_psych_design_public_release.py --phase authorization",
        "python tools/build_psych_design_companion_asset.py",
        "python -m build --no-isolation",
        "--phase distributions",
        "pypa/gh-action-pypi-publish@release/v1",
        "print-hash: true",
    )
    for token in required:
        if token not in text:
            fail(f"publication workflow is missing gate: {token}")
    if "push:" in text:
        fail("publication workflow must remain manual")
    if "psych-design-companion-v0-1-candidate" in text:
        fail("candidate tag is wired into publication workflow")


def verify_release_documentation() -> None:
    notes = RELEASE_NOTES.read_text(encoding="utf-8")
    if "v0.26.0 — Psychological Statistics by Design companion v0.1" not in notes:
        fail("release notes do not declare v0.26.0")
    if "v0.26.0 release candidate" in notes:
        fail("release notes still label v0.26.0 as a candidate")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if 'pystatsv1[psych-design]==0.26.0' not in readme:
        fail("README does not expose the exact public install route")
    if "synthetic-only" not in readme.lower():
        fail("README lost the synthetic-only boundary")


def verify_pending_public_receipt() -> None:
    receipt = load(PUBLIC_RECEIPT)
    if receipt.get("schema_version") != (
        "pystatsv1-psych-design-public-release-v0.1"
    ):
        fail("public-release receipt schema changed")
    if receipt.get("status") not in (
        "owner_authorized_pending_publication",
        "public_release_verified",
    ):
        fail("public-release receipt has an invalid lifecycle status")
    if receipt.get("package_version") != EXPECTED_VERSION:
        fail("public-release receipt version changed")
    state = receipt.get("authorization_state", {})
    if state.get("pypi_release_authorized") is not True:
        fail("public-release receipt does not retain PyPI authorization")
    for gate in CLOSED_GATES:
        if state.get(gate) is not False:
            fail(f"public-release receipt opens closed gate: {gate}")


def verify_public_receipt(auth: dict[str, Any]) -> None:
    receipt = load(PUBLIC_RECEIPT)
    if receipt.get("status") != "public_release_verified":
        fail("public release has not been verified")
    if receipt.get("public_artifacts_verified") is not True:
        fail("public artifacts are not verified")
    if receipt.get("trusted_publisher") is not True:
        fail("public receipt does not record trusted publishing")
    if receipt.get("scientific_candidate_unchanged") is not True:
        fail("public receipt does not preserve the scientific candidate")
    release_commit = receipt.get("release_commit")
    if not isinstance(release_commit, str) or len(release_commit) != 40:
        fail("public receipt release commit is invalid")
    tagged_commit = verify_release_tag(auth, required=True)
    if tagged_commit != release_commit:
        fail("public receipt release commit differs from v0.26.0")
    if not str(receipt.get("tag_ci_run_id", "")).isdigit():
        fail("public receipt tag CI run ID is invalid")
    if not str(receipt.get("publish_workflow_run_id", "")).isdigit():
        fail("public receipt publish run ID is invalid")
    artifacts = receipt.get("artifacts", {})
    verifier = load_verifier_module()
    for key, filename in (
        ("wheel", verifier.EXPECTED_WHEEL),
        ("sdist", verifier.EXPECTED_SDIST),
    ):
        row = artifacts.get(key, {})
        if row.get("filename") != filename:
            fail(f"public receipt {key} filename changed")
        digest = row.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            fail(f"public receipt {key} hash is invalid")
        if row.get("embedded_asset_sha256") != EXPECTED_ASSET_SHA256:
            fail(f"public receipt {key} asset hash changed")
    if artifacts.get("embedded_asset_identity_exact") is not True:
        fail("public wheel and sdist asset identities differ")
    smoke = receipt.get("reader_smoke", {})
    if smoke.get("status") != "pass":
        fail("public reader smoke did not pass")
    if smoke.get("installed_version") != EXPECTED_VERSION:
        fail("public reader smoke installed the wrong version")
    if smoke.get("installed_asset_sha256") != EXPECTED_ASSET_SHA256:
        fail("public reader smoke installed the wrong asset")
    if not all(smoke.get("command_status", {}).values()):
        fail("public reader smoke missed a command")
    if not all(smoke.get("first_result_outputs", {}).values()):
        fail("public reader smoke missed first-result output")
    if smoke.get("absolute_workspace_path_recorded") is not False:
        fail("public receipt records an absolute smoke workspace")


def verify_distribution_phase(dist_dir: Path) -> None:
    verifier = load_verifier_module()
    summary = verifier.inspect_distribution_directory(dist_dir)
    if summary.get("embedded_asset_identity_exact") is not True:
        fail("built wheel and sdist do not share the governed asset")


def verify_common(auth: dict[str, Any]) -> None:
    if project_version() != EXPECTED_VERSION:
        fail("pyproject version is not 0.26.0")
    verify_authorization_document(auth)
    verify_technical_readiness()
    verify_frozen_asset()
    verify_release_source_paths(auth)
    verify_proof_tag()
    verify_publication_workflow()
    verify_release_documentation()
    verify_pending_public_receipt()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("source", "authorization", "distributions", "public"),
        default="source",
    )
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        auth = load(AUTHORIZATION)
        verify_common(auth)
        if args.phase == "authorization":
            verify_release_tag(auth, required=False)
        elif args.phase == "distributions":
            verify_release_tag(auth, required=True)
            verify_distribution_phase(args.dist_dir)
        elif args.phase == "public":
            verify_public_receipt(auth)
    except (OSError, PublicReleaseCheckError) as exc:
        print(f"PYSTATSV1_PUBLIC_RELEASE_CHECK_ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        "PYSTATSV1_PUBLIC_RELEASE_CHECK_OK "
        f"phase={args.phase} package=pystatsv1 version=0.26.0 "
        "pypi_authorized=true portal=false book=false real_data=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
