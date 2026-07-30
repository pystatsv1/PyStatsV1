#!/usr/bin/env python3
"""Compare native-Ubuntu and WSL clean-reader receipts and freeze readiness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid proof receipt {path}: {exc}") from exc


def write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def add(checks: list[dict[str, Any]], name: str, left: Any, right: Any) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if left == right else "fail",
            "ubuntu": left,
            "wsl": right,
        }
    )


def validate(receipt: dict[str, Any], role: str) -> None:
    if receipt.get("schema_version") != "pystatsv1-psych-design-clean-reader-proof-v0.1":
        raise SystemExit(f"{role} receipt schema is unsupported")
    if receipt.get("status") != "pass" or receipt.get("platform_role") != role:
        raise SystemExit(f"{role} receipt does not record a passing {role} proof")
    if receipt.get("synthetic_only") is not True:
        raise SystemExit(f"{role} receipt lost the synthetic-only boundary")
    if receipt.get("real_data_authorized") is not False:
        raise SystemExit(f"{role} receipt authorizes real data")
    if sorted(receipt.get("study_evidence", {})) != EXPECTED_STUDIES:
        raise SystemExit(f"{role} receipt does not cover all ten studies")
    if not all(receipt.get("command_markers", {}).values()):
        raise SystemExit(f"{role} receipt contains a missing success marker")
    gates = receipt.get("publication_gates", {})
    if any(gates.get(key) is not False for key in (
        "pypi_release_authorized",
        "portal_release_authorized",
        "book_binding_authorized",
        "real_data_authorized",
    )):
        raise SystemExit(f"{role} receipt opens a closed release gate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ubuntu", type=Path, required=True)
    parser.add_argument("--wsl", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--readiness", type=Path, required=True)
    args = parser.parse_args()

    ubuntu = load(args.ubuntu)
    wsl = load(args.wsl)
    validate(ubuntu, "ubuntu")
    validate(wsl, "wsl")
    checks: list[dict[str, Any]] = []

    for key in (
        "candidate_commit",
        "candidate_tag",
        "package_version",
        "companion_version",
    ):
        add(checks, key, ubuntu[key], wsl[key])
    for key in (
        "wheel_name",
        "wheel_sha256",
        "wheel_bytes",
        "asset_sha256",
        "asset_bytes",
        "source_manifest_sha256",
        "study_index_sha256",
        "source_file_count",
        "source_manifest_status",
    ):
        add(
            checks,
            f"artifact_identity.{key}",
            ubuntu["artifact_identity"][key],
            wsl["artifact_identity"][key],
        )
    add(checks, "source_bindings", ubuntu["source_bindings"], wsl["source_bindings"])

    png_differences: dict[str, Any] = {}
    for study in EXPECTED_STUDIES:
        left = ubuntu["study_evidence"][study]
        right = wsl["study_evidence"][study]
        for key in (
            "verification_category",
            "python_reported_fields",
            "r_metrics",
            "verification_status",
            "verification_comparisons",
            "v4_documented_not_equal_fields",
            "reviewer_packet_membership",
            "reviewer_packet_file_count",
            "reviewer_packet_source_hashes",
            "apa_runtime_binding_sha256",
            "matched_limitation_runtime_sha256",
        ):
            add(checks, f"{study}.{key}", left[key], right[key])
        add(
            checks,
            f"{study}.figure_semantics",
            left["figures"]["manifest_semantics"],
            right["figures"]["manifest_semantics"],
        )
        png_equal = left["figures"]["png_hashes"] == right["figures"]["png_hashes"]
        png_differences[study] = {
            "byte_identical": png_equal,
            "ubuntu": left["figures"]["png_hashes"],
            "wsl": right["figures"]["png_hashes"],
            "status": "identical" if png_equal else "allowed_renderer_difference",
        }

    failed = [row["name"] for row in checks if row["status"] != "pass"]
    comparison = {
        "schema_version": "pystatsv1-psych-design-cross-platform-comparison-v0.1",
        "candidate_commit": ubuntu["candidate_commit"],
        "package_version": ubuntu["package_version"],
        "companion_version": ubuntu["companion_version"],
        "status": "pass" if not failed else "fail",
        "exact_check_count": len(checks),
        "failed_exact_checks": failed,
        "exact_checks": checks,
        "png_renderer_comparison": {
            "png_byte_identity_required": False,
            "scientific_figure_semantics_required_exact": True,
            "studies": png_differences,
        },
        "synthetic_only": True,
        "real_data_authorized": False,
    }
    write(args.comparison, comparison)

    ready = not failed
    readiness = {
        "schema_version": "pystatsv1-psych-design-release-readiness-v0.1",
        "candidate_commit": ubuntu["candidate_commit"],
        "package_version": ubuntu["package_version"],
        "companion_version": ubuntu["companion_version"],
        "candidate_implementation_passed": True,
        "clean_ubuntu_proof_passed": True,
        "clean_wsl_proof_passed": True,
        "cross_platform_comparison_passed": ready,
        "technical_release_ready": ready,
        "pypi_release_authorized": False,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
        "status": "technical_release_ready_not_authorized" if ready else "cross_platform_comparison_failed",
    }
    write(args.readiness, readiness)
    if failed:
        raise SystemExit("cross-platform proof mismatch:\n" + "\n".join(failed))
    print(
        "PYSTATSV1_PSYCH_DESIGN_CROSS_PLATFORM_COMPARISON_OK "
        f"checks={len(checks)} png_byte_identity_required=false"
    )


if __name__ == "__main__":
    main()
