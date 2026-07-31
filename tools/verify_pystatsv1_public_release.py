#!/usr/bin/env python3
"""Verify public PyPI artifacts and a fresh PyStatsV1 0.26.0 reader route."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from email.parser import Parser
from pathlib import Path, PurePosixPath
from typing import Any

PACKAGE_NAME = "pystatsv1"
PACKAGE_VERSION = "0.26.0"
RELEASE_TAG = "v0.26.0"
PROOF_TAG = "psych-design-companion-v0-1-release-proof"
EXPECTED_WHEEL = "pystatsv1-0.26.0-py3-none-any.whl"
EXPECTED_SDIST = "pystatsv1-0.26.0.tar.gz"
ASSET_MEMBER = "pystatsv1/assets/psychological_statistics_by_design_companion_v0_1.zip"
SDIST_ASSET_SUFFIX = "src/pystatsv1/assets/psychological_statistics_by_design_companion_v0_1.zip"
ASSET_SHA256 = "bd0932c1d126758f37fab180173d6b95b5e4c31bc654724251aa6eb6296243c1"
ASSET_BYTES = 136801
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/{PACKAGE_VERSION}/json"
PYPI_INDEX_URL = "https://pypi.org/simple"
PUBLIC_RECEIPT_SCHEMA = "pystatsv1-psych-design-public-release-v0.1"


class PublicReleaseError(RuntimeError):
    """Raised when a public release artifact or smoke check is invalid."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _safe_archive_name(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise PublicReleaseError(f"unsafe archive member path: {name!r}")


def _metadata_fields(text: str) -> dict[str, str]:
    message = Parser().parsestr(text)
    return {key: value for key, value in message.items()}


def inspect_wheel(path: Path) -> dict[str, Any]:
    """Return a strict identity summary for the public wheel."""
    if path.name != EXPECTED_WHEEL:
        raise PublicReleaseError(f"unexpected wheel filename: {path.name}")
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            for name in names:
                _safe_archive_name(name)
            metadata_names = [
                name
                for name in names
                if name.endswith(".dist-info/METADATA")
            ]
            if metadata_names != ["pystatsv1-0.26.0.dist-info/METADATA"]:
                raise PublicReleaseError(
                    f"unexpected wheel metadata members: {metadata_names}"
                )
            metadata = _metadata_fields(
                archive.read(metadata_names[0]).decode("utf-8")
            )
            if metadata.get("Name") != PACKAGE_NAME:
                raise PublicReleaseError("wheel package name is not pystatsv1")
            if metadata.get("Version") != PACKAGE_VERSION:
                raise PublicReleaseError("wheel package version is not 0.26.0")
            if ASSET_MEMBER not in names:
                raise PublicReleaseError("wheel is missing the governed companion asset")
            asset = archive.read(ASSET_MEMBER)
            if len(asset) != ASSET_BYTES:
                raise PublicReleaseError("wheel companion asset byte size changed")
            if sha256_bytes(asset) != ASSET_SHA256:
                raise PublicReleaseError("wheel companion asset hash changed")
            if "pystatsv1-0.26.0.dist-info/RECORD" not in names:
                raise PublicReleaseError("wheel RECORD is missing")
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
        raise PublicReleaseError(f"invalid wheel: {exc}") from exc
    return {
        "filename": path.name,
        "packagetype": "bdist_wheel",
        "python_tag": "py3",
        "abi_tag": "none",
        "platform_tag": "any",
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "member_count": len(names),
        "metadata_name": metadata["Name"],
        "metadata_version": metadata["Version"],
        "embedded_asset_member": ASSET_MEMBER,
        "embedded_asset_bytes": len(asset),
        "embedded_asset_sha256": sha256_bytes(asset),
    }


def inspect_sdist(path: Path) -> dict[str, Any]:
    """Return a strict identity summary for the public source distribution."""
    if path.name != EXPECTED_SDIST:
        raise PublicReleaseError(f"unexpected sdist filename: {path.name}")
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            for member in members:
                _safe_archive_name(member.name)
                if member.issym() or member.islnk():
                    raise PublicReleaseError(
                        f"sdist contains a link member: {member.name}"
                    )
            roots = {PurePosixPath(name).parts[0] for name in names if name}
            if roots != {"pystatsv1-0.26.0"}:
                raise PublicReleaseError(f"unexpected sdist root: {sorted(roots)}")
            pyproject_name = "pystatsv1-0.26.0/pyproject.toml"
            pkg_info_name = "pystatsv1-0.26.0/PKG-INFO"
            asset_name = f"pystatsv1-0.26.0/{SDIST_ASSET_SUFFIX}"
            for required in (pyproject_name, pkg_info_name, asset_name):
                if required not in names:
                    raise PublicReleaseError(f"sdist is missing {required}")
            pkg_file = archive.extractfile(pkg_info_name)
            asset_file = archive.extractfile(asset_name)
            if pkg_file is None or asset_file is None:
                raise PublicReleaseError("sdist required member could not be read")
            metadata = _metadata_fields(pkg_file.read().decode("utf-8"))
            asset = asset_file.read()
            if metadata.get("Name") != PACKAGE_NAME:
                raise PublicReleaseError("sdist package name is not pystatsv1")
            if metadata.get("Version") != PACKAGE_VERSION:
                raise PublicReleaseError("sdist package version is not 0.26.0")
            if len(asset) != ASSET_BYTES or sha256_bytes(asset) != ASSET_SHA256:
                raise PublicReleaseError("sdist companion asset identity changed")
    except (OSError, tarfile.TarError, UnicodeDecodeError) as exc:
        raise PublicReleaseError(f"invalid sdist: {exc}") from exc
    return {
        "filename": path.name,
        "packagetype": "sdist",
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "member_count": len(members),
        "metadata_name": metadata["Name"],
        "metadata_version": metadata["Version"],
        "embedded_asset_member": SDIST_ASSET_SUFFIX,
        "embedded_asset_bytes": len(asset),
        "embedded_asset_sha256": sha256_bytes(asset),
    }


def inspect_distribution_directory(dist_dir: Path) -> dict[str, Any]:
    """Inspect exactly one expected wheel and one expected sdist."""
    dist_dir = dist_dir.resolve()
    files = sorted(path for path in dist_dir.iterdir() if path.is_file())
    expected = {EXPECTED_WHEEL, EXPECTED_SDIST}
    actual = {path.name for path in files}
    if actual != expected:
        raise PublicReleaseError(
            f"distribution directory must contain exactly {sorted(expected)}; "
            f"found {sorted(actual)}"
        )
    wheel = inspect_wheel(dist_dir / EXPECTED_WHEEL)
    sdist = inspect_sdist(dist_dir / EXPECTED_SDIST)
    return {
        "wheel": wheel,
        "sdist": sdist,
        "embedded_asset_identity_exact": (
            wheel["embedded_asset_sha256"]
            == sdist["embedded_asset_sha256"]
            == ASSET_SHA256
        ),
    }


def _fetch_json(url: str, *, timeout_seconds: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PyStatsV1-Dropin-035-public-verifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_pypi_release(
    *, timeout_seconds: int, poll_seconds: int
) -> dict[str, Any]:
    """Wait for the exact PyPI release JSON to become publicly available."""
    deadline = time.monotonic() + timeout_seconds
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            payload = _fetch_json(PYPI_JSON_URL, timeout_seconds=30)
            if payload.get("info", {}).get("version") == PACKAGE_VERSION:
                return payload
            last_error = "PyPI JSON returned the wrong version"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = str(exc)
        time.sleep(poll_seconds)
    raise PublicReleaseError(
        f"PyPI release did not become available within {timeout_seconds}s: {last_error}"
    )


def pypi_version_exists(*, timeout_seconds: int = 30) -> bool:
    """Return whether the exact package version already exists on PyPI."""
    try:
        payload = _fetch_json(PYPI_JSON_URL, timeout_seconds=timeout_seconds)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise PublicReleaseError(f"PyPI version check failed: {exc}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise PublicReleaseError(f"PyPI version check failed: {exc}") from exc
    return payload.get("info", {}).get("version") == PACKAGE_VERSION


def _download(url: str, destination: Path, expected_sha256: str) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PyStatsV1-Dropin-035-public-verifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    digest = sha256_bytes(payload)
    if digest != expected_sha256:
        raise PublicReleaseError(
            f"download hash mismatch for {destination.name}: {digest}"
        )
    destination.write_bytes(payload)


def download_public_distributions(
    payload: dict[str, Any], destination: Path
) -> dict[str, Any]:
    """Download the exact wheel and sdist reported by PyPI."""
    destination.mkdir(parents=True, exist_ok=True)
    urls = payload.get("urls", [])
    records = {row.get("filename"): row for row in urls}
    if set(records) != {EXPECTED_WHEEL, EXPECTED_SDIST}:
        raise PublicReleaseError(
            "PyPI release must expose exactly the expected wheel and sdist; "
            f"found {sorted(records)}"
        )
    for filename, row in records.items():
        expected_type = "bdist_wheel" if filename == EXPECTED_WHEEL else "sdist"
        if row.get("packagetype") != expected_type:
            raise PublicReleaseError(f"unexpected PyPI package type for {filename}")
        digest = row.get("digests", {}).get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise PublicReleaseError(f"PyPI did not report a SHA-256 for {filename}")
        _download(row["url"], destination / filename, digest)
    inspected = inspect_distribution_directory(destination)
    for key in ("wheel", "sdist"):
        filename = inspected[key]["filename"]
        if inspected[key]["sha256"] != records[filename]["digests"]["sha256"]:
            raise PublicReleaseError(f"PyPI metadata hash mismatch for {filename}")
        inspected[key]["pypi_upload_time_iso_8601"] = records[filename].get(
            "upload_time_iso_8601"
        )
        inspected[key]["requires_python"] = records[filename].get("requires_python")
    return inspected


def _run(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    marker: str | None = None,
) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise PublicReleaseError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}"
        )
    if marker is not None and marker not in completed.stdout:
        raise PublicReleaseError(
            f"command did not emit required marker {marker!r}: {' '.join(command)}"
        )
    return completed.stdout


def _venv_paths(venv: Path) -> tuple[Path, Path]:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe", venv / "Scripts" / "pystatsv1.exe"
    return venv / "bin" / "python", venv / "bin" / "pystatsv1"


def run_public_reader_smoke(work_root: Path) -> dict[str, Any]:
    """Install from public PyPI in a fresh venv and run the first-result route."""
    if shutil.which("make") is None:
        raise PublicReleaseError("make is required for the public first-result smoke")
    if shutil.which("Rscript") is None:
        raise PublicReleaseError("Rscript is required for the public first-result smoke")

    venv = work_root / ".venv"
    workspace = work_root / "reader" / "psychological_statistics_by_design_companion_v0_1"
    _run([sys.executable, "-m", "venv", str(venv)])
    python, cli = _venv_paths(venv)
    _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    install_output = _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--index-url",
            PYPI_INDEX_URL,
            f"{PACKAGE_NAME}[psych-design]=={PACKAGE_VERSION}",
        ]
    )
    identity_output = _run(
        [
            str(python),
            "-c",
            (
                "from importlib import metadata, resources; "
                "import hashlib, json; "
                "p=resources.files('pystatsv1.assets')/"
                "'psychological_statistics_by_design_companion_v0_1.zip'; "
                "b=p.read_bytes(); "
                "print(json.dumps({'version': metadata.version('pystatsv1'), "
                "'asset_sha256': hashlib.sha256(b).hexdigest(), "
                "'asset_bytes': len(b)}, sort_keys=True))"
            ),
        ]
    )
    installed_identity = json.loads(identity_output.strip().splitlines()[-1])
    if installed_identity != {
        "version": PACKAGE_VERSION,
        "asset_sha256": ASSET_SHA256,
        "asset_bytes": ASSET_BYTES,
    }:
        raise PublicReleaseError(
            f"installed public package identity mismatch: {installed_identity}"
        )

    info_output = _run([str(cli), "psych-design", "info"])
    _run(
        [
            str(cli),
            "psych-design",
            "init",
            "--dest",
            str(workspace),
        ]
    )
    verify_before = _run(
        [str(cli), "psych-design", "verify", "--dest", str(workspace)],
        marker="PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
    )
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "-r",
            str(workspace / "requirements-psych-design-companion.txt"),
        ]
    )
    doctor_output = _run(
        [str(cli), "psych-design", "doctor", "--dest", str(workspace)],
        marker="PYSTATSV1_PSYCH_DESIGN_DOCTOR_OK",
    )
    smoke_env = os.environ.copy()
    smoke_env["PYTHON"] = str(python)
    first_result_output = _run(
        ["make", "first-result", f"PYTHON={python}"],
        cwd=workspace,
        env=smoke_env,
        marker="PYSTATSV1_PSYCH_DESIGN_FIRST_RESULT_OK",
    )
    verify_after = _run(
        [str(cli), "psych-design", "verify", "--dest", str(workspace)],
        marker="PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
    )
    required_outputs = [
        workspace / "outputs" / "swl_s02" / "python_result.json",
        workspace / "outputs" / "swl_s02" / "r_result.csv",
        workspace / "outputs" / "swl_s02" / "verification_receipt.json",
        workspace / "outputs" / "swl_s02" / "figures" / "FIGURE_MANIFEST.json",
        workspace / "outputs" / "swl_s02" / "reviewer_packet" / "MANIFEST.json",
    ]
    missing = [path.name for path in required_outputs if not path.exists()]
    if missing:
        raise PublicReleaseError(f"public first-result smoke missed outputs: {missing}")

    return {
        "status": "pass",
        "fresh_virtual_environment": True,
        "public_index": PYPI_INDEX_URL,
        "installed_version": installed_identity["version"],
        "installed_asset_sha256": installed_identity["asset_sha256"],
        "installed_asset_bytes": installed_identity["asset_bytes"],
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "rscript_version": _run(["Rscript", "--version"]).strip(),
        "command_status": {
            "pip_install_public_exact": "Successfully installed" in install_output,
            "psych_design_info": "Companion version: v0.1" in info_output,
            "psych_design_init": True,
            "verify_before": "PYSTATSV1_PSYCH_DESIGN_VERIFY_OK" in verify_before,
            "doctor": "PYSTATSV1_PSYCH_DESIGN_DOCTOR_OK" in doctor_output,
            "first_result": "PYSTATSV1_PSYCH_DESIGN_FIRST_RESULT_OK"
            in first_result_output,
            "verify_after": "PYSTATSV1_PSYCH_DESIGN_VERIFY_OK" in verify_after,
        },
        "first_result_outputs": {
            "python_result": True,
            "r_result": True,
            "verification_receipt": True,
            "figure_manifest": True,
            "reviewer_packet": True,
        },
        "absolute_workspace_path_recorded": False,
    }


def build_public_receipt(
    *,
    release_commit: str,
    tag_ci_run_id: str,
    publish_workflow_run_id: str,
    distributions: dict[str, Any],
    smoke: dict[str, Any],
) -> dict[str, Any]:
    if not release_commit or len(release_commit) != 40:
        raise PublicReleaseError("release commit must be a full 40-character SHA")
    if not all(smoke.get("command_status", {}).values()):
        raise PublicReleaseError("public reader smoke did not pass every command")
    return {
        "schema_version": PUBLIC_RECEIPT_SCHEMA,
        "status": "public_release_verified",
        "verified_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "package_name": PACKAGE_NAME,
        "package_version": PACKAGE_VERSION,
        "companion_version": "v0.1",
        "release_tag": RELEASE_TAG,
        "release_commit": release_commit,
        "proof_tag": PROOF_TAG,
        "tag_ci_run_id": str(tag_ci_run_id),
        "publish_workflow_run_id": str(publish_workflow_run_id),
        "trusted_publisher": True,
        "public_index": PYPI_INDEX_URL,
        "pypi_project": f"https://pypi.org/project/{PACKAGE_NAME}/{PACKAGE_VERSION}/",
        "public_artifacts_verified": True,
        "artifacts": distributions,
        "reader_smoke": smoke,
        "authorization_state": {
            "pypi_release_authorized": True,
            "portal_release_authorized": False,
            "book_binding_authorized": False,
            "real_data_authorized": False,
        },
        "scientific_candidate_unchanged": True,
        "embedded_asset_sha256": ASSET_SHA256,
        "embedded_asset_bytes": ASSET_BYTES,
    }


def verify_public_release(
    *,
    output: Path,
    release_commit: str,
    tag_ci_run_id: str,
    publish_workflow_run_id: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> dict[str, Any]:
    payload = wait_for_pypi_release(
        timeout_seconds=timeout_seconds, poll_seconds=poll_seconds
    )
    with tempfile.TemporaryDirectory(prefix="pystatsv1-public-release-") as temp:
        root = Path(temp)
        distributions = download_public_distributions(payload, root / "dist")
        smoke = run_public_reader_smoke(root / "smoke")
    receipt = build_public_receipt(
        release_commit=release_commit,
        tag_ci_run_id=tag_ci_run_id,
        publish_workflow_run_id=publish_workflow_run_id,
        distributions=distributions,
        smoke=smoke,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-absent", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--release-commit")
    parser.add_argument("--tag-ci-run-id")
    parser.add_argument("--publish-workflow-run-id")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-seconds", type=int, default=15)
    args = parser.parse_args()
    try:
        if args.expect_absent:
            if pypi_version_exists():
                raise PublicReleaseError(
                    f"{PACKAGE_NAME} {PACKAGE_VERSION} already exists on PyPI"
                )
            print(
                "PYSTATSV1_PUBLIC_RELEASE_ABSENCE_OK "
                f"package={PACKAGE_NAME} version={PACKAGE_VERSION}"
            )
            return 0
        required = {
            "--output": args.output,
            "--release-commit": args.release_commit,
            "--tag-ci-run-id": args.tag_ci_run_id,
            "--publish-workflow-run-id": args.publish_workflow_run_id,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise PublicReleaseError(
                f"missing required public-verification arguments: {', '.join(missing)}"
            )
        receipt = verify_public_release(
            output=args.output,
            release_commit=args.release_commit,
            tag_ci_run_id=args.tag_ci_run_id,
            publish_workflow_run_id=args.publish_workflow_run_id,
            timeout_seconds=args.timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
    except (OSError, PublicReleaseError) as exc:
        print(f"PYSTATSV1_PUBLIC_RELEASE_VERIFY_ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        "PYSTATSV1_PUBLIC_RELEASE_VERIFY_OK "
        f"version={receipt['package_version']} "
        f"wheel={receipt['artifacts']['wheel']['sha256']} "
        f"sdist={receipt['artifacts']['sdist']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
