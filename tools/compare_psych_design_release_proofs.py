#!/usr/bin/env python3
"""Compare native-Ubuntu and WSL clean-reader receipts and freeze readiness."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]
COMPARISON_CANONICAL_FIELDS = (
    "field",
    "python",
    "r",
    "allowed_absolute_difference",
    "status",
)
ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT = "1e-12"
ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE = Decimal(
    ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT
)
GENERATED_RUNTIME_EVIDENCE_FILES = (
    "R_RESULT.csv",
    "VERIFICATION_RECEIPT.json",
)


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


def add(checks: list[dict[str, Any]], name: str, left: Any, right: Any) -> bool:
    passed = left == right
    checks.append(
        {
            "name": name,
            "status": "pass" if passed else "fail",
            "ubuntu": left,
            "wsl": right,
        }
    )
    return passed


def add_required_value(
    checks: list[dict[str, Any]],
    name: str,
    actual: Any,
    required: Any,
    role: str,
) -> bool:
    passed = actual == required
    checks.append(
        {
            "name": name,
            "status": "pass" if passed else "fail",
            role: actual,
            "required": required,
        }
    )
    return passed


def decimal_value(value: Any, label: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric: {value!r}") from exc


def decimal_text(value: Decimal) -> str:
    return str(value).replace("E", "e")


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
    if any(
        gates.get(key) is not False
        for key in (
            "pypi_release_authorized",
            "portal_release_authorized",
            "book_binding_authorized",
            "real_data_authorized",
        )
    ):
        raise SystemExit(f"{role} receipt opens a closed release gate")


def compare_verification_comparisons(
    checks: list[dict[str, Any]],
    study: str,
    left_rows: Any,
    right_rows: Any,
) -> dict[str, Any]:
    prefix = f"{study}.verification_comparisons"
    details: dict[str, Any] = {
        "canonical_fields_required_exact": list(COMPARISON_CANONICAL_FIELDS),
        "both_statuses_required": "pass",
        "absolute_difference_serialization_tolerance": (
            ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT
        ),
        "fields": [],
    }
    start = len(checks)

    left_is_list = isinstance(left_rows, list)
    right_is_list = isinstance(right_rows, list)
    add_required_value(
        checks,
        f"{prefix}.ubuntu_is_list",
        left_is_list,
        True,
        "ubuntu",
    )
    add_required_value(
        checks,
        f"{prefix}.wsl_is_list",
        right_is_list,
        True,
        "wsl",
    )
    if not left_is_list or not right_is_list:
        details["status"] = "fail"
        details["maximum_observed_absolute_difference_delta"] = None
        return details

    left_fields = [
        row.get("field") if isinstance(row, dict) else None for row in left_rows
    ]
    right_fields = [
        row.get("field") if isinstance(row, dict) else None for row in right_rows
    ]
    add(checks, f"{prefix}.field_sequence", left_fields, right_fields)
    add_required_value(
        checks,
        f"{prefix}.ubuntu_fields_unique",
        len(left_fields) == len(set(left_fields)),
        True,
        "ubuntu",
    )
    add_required_value(
        checks,
        f"{prefix}.wsl_fields_unique",
        len(right_fields) == len(set(right_fields)),
        True,
        "wsl",
    )

    left_by_field = {
        row.get("field"): row
        for row in left_rows
        if isinstance(row, dict) and row.get("field") is not None
    }
    right_by_field = {
        row.get("field"): row
        for row in right_rows
        if isinstance(row, dict) and row.get("field") is not None
    }
    ordered_fields = list(dict.fromkeys(left_fields + right_fields))
    observed_deltas: list[Decimal] = []

    for field in ordered_fields:
        label = str(field)
        left = left_by_field.get(field)
        right = right_by_field.get(field)
        left_present = isinstance(left, dict)
        right_present = isinstance(right, dict)
        add_required_value(
            checks,
            f"{prefix}.{label}.ubuntu_present",
            left_present,
            True,
            "ubuntu",
        )
        add_required_value(
            checks,
            f"{prefix}.{label}.wsl_present",
            right_present,
            True,
            "wsl",
        )
        field_detail: dict[str, Any] = {"field": field}
        if not left_present or not right_present:
            field_detail["status"] = "fail"
            details["fields"].append(field_detail)
            continue

        canonical_exact = True
        for key in COMPARISON_CANONICAL_FIELDS:
            canonical_exact = (
                add(
                    checks,
                    f"{prefix}.{label}.{key}",
                    left.get(key),
                    right.get(key),
                )
                and canonical_exact
            )
        left_pass = add_required_value(
            checks,
            f"{prefix}.{label}.ubuntu_status_pass",
            left.get("status"),
            "pass",
            "ubuntu",
        )
        right_pass = add_required_value(
            checks,
            f"{prefix}.{label}.wsl_status_pass",
            right.get("status"),
            "pass",
            "wsl",
        )

        try:
            left_difference = decimal_value(
                left.get("absolute_difference"),
                f"{prefix}.{label}.ubuntu.absolute_difference",
            )
            right_difference = decimal_value(
                right.get("absolute_difference"),
                f"{prefix}.{label}.wsl.absolute_difference",
            )
            left_allowed = decimal_value(
                left.get("allowed_absolute_difference"),
                f"{prefix}.{label}.ubuntu.allowed_absolute_difference",
            )
            right_allowed = decimal_value(
                right.get("allowed_absolute_difference"),
                f"{prefix}.{label}.wsl.allowed_absolute_difference",
            )
        except ValueError as exc:
            checks.append(
                {
                    "name": f"{prefix}.{label}.numeric_serialization",
                    "status": "fail",
                    "ubuntu": left.get("absolute_difference"),
                    "wsl": right.get("absolute_difference"),
                    "error": str(exc),
                }
            )
            field_detail.update(
                {
                    "ubuntu_absolute_difference": left.get("absolute_difference"),
                    "wsl_absolute_difference": right.get("absolute_difference"),
                    "status": "fail",
                    "error": str(exc),
                }
            )
            details["fields"].append(field_detail)
            continue

        left_in_bounds = left_difference <= left_allowed
        right_in_bounds = right_difference <= right_allowed
        add_required_value(
            checks,
            f"{prefix}.{label}.ubuntu_difference_within_registered_tolerance",
            left_in_bounds,
            True,
            "ubuntu",
        )
        add_required_value(
            checks,
            f"{prefix}.{label}.wsl_difference_within_registered_tolerance",
            right_in_bounds,
            True,
            "wsl",
        )
        observed_delta = abs(left_difference - right_difference)
        observed_deltas.append(observed_delta)
        serialization_passed = (
            observed_delta <= ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE
        )
        checks.append(
            {
                "name": f"{prefix}.{label}.absolute_difference_serialization",
                "status": "pass" if serialization_passed else "fail",
                "ubuntu": decimal_text(left_difference),
                "wsl": decimal_text(right_difference),
                "observed_delta": decimal_text(observed_delta),
                "allowed_cross_platform_delta": (
                    ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT
                ),
            }
        )
        field_passed = all(
            (
                canonical_exact,
                left_pass,
                right_pass,
                left_in_bounds,
                right_in_bounds,
                serialization_passed,
            )
        )
        field_detail.update(
            {
                "ubuntu_absolute_difference": decimal_text(left_difference),
                "wsl_absolute_difference": decimal_text(right_difference),
                "observed_delta": decimal_text(observed_delta),
                "allowed_cross_platform_delta": (
                    ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT
                ),
                "status": "pass" if field_passed else "fail",
            }
        )
        details["fields"].append(field_detail)

    maximum = max(observed_deltas) if observed_deltas else None
    details["maximum_observed_absolute_difference_delta"] = (
        decimal_text(maximum) if maximum is not None else None
    )
    details["status"] = (
        "pass"
        if all(row["status"] == "pass" for row in checks[start:])
        else "fail"
    )
    return details


def compare_reviewer_packet_hashes(
    checks: list[dict[str, Any]],
    study: str,
    left_hashes: Any,
    right_hashes: Any,
    prerequisites: dict[str, bool],
) -> dict[str, Any]:
    prefix = f"{study}.reviewer_packet_source_hashes"
    start = len(checks)
    left_is_dict = isinstance(left_hashes, dict)
    right_is_dict = isinstance(right_hashes, dict)
    add_required_value(
        checks,
        f"{prefix}.ubuntu_is_object",
        left_is_dict,
        True,
        "ubuntu",
    )
    add_required_value(
        checks,
        f"{prefix}.wsl_is_object",
        right_is_dict,
        True,
        "wsl",
    )
    if not left_is_dict or not right_is_dict:
        return {
            "status": "fail",
            "allowed_different_files": list(GENERATED_RUNTIME_EVIDENCE_FILES),
            "prerequisites": prerequisites,
            "files": {},
        }

    left_names = sorted(left_hashes)
    right_names = sorted(right_hashes)
    names_exact = add(checks, f"{prefix}.membership", left_names, right_names)
    immutable_names = sorted(
        name
        for name in set(left_names) | set(right_names)
        if name not in GENERATED_RUNTIME_EVIDENCE_FILES
    )
    immutable_left = {name: left_hashes.get(name) for name in immutable_names}
    immutable_right = {name: right_hashes.get(name) for name in immutable_names}
    immutable_exact = add(
        checks,
        f"{prefix}.immutable_hashes",
        immutable_left,
        immutable_right,
    )

    runtime_prerequisites = {
        **prerequisites,
        "hash_membership_exact": names_exact,
        "immutable_hashes_exact": immutable_exact,
    }
    prerequisites_passed = all(runtime_prerequisites.values())
    files: dict[str, Any] = {}
    for name in GENERATED_RUNTIME_EVIDENCE_FILES:
        ubuntu_hash = left_hashes.get(name)
        wsl_hash = right_hashes.get(name)
        present = ubuntu_hash is not None and wsl_hash is not None
        add_required_value(
            checks,
            f"{prefix}.{name}.present_in_both",
            present,
            True,
            "observed",
        )
        identical = present and ubuntu_hash == wsl_hash
        if identical:
            status = "identical"
        elif present and prerequisites_passed:
            status = "allowed_generated_runtime_evidence_difference"
        else:
            status = "blocked_by_canonical_or_source_mismatch"
        files[name] = {
            "ubuntu_sha256": ubuntu_hash,
            "wsl_sha256": wsl_hash,
            "byte_identical": identical,
            "status": status,
        }

    allowed_or_identical = all(
        row["status"]
        in {
            "identical",
            "allowed_generated_runtime_evidence_difference",
        }
        for row in files.values()
    )
    add_required_value(
        checks,
        f"{prefix}.generated_runtime_differences_policy",
        allowed_or_identical,
        True,
        "observed",
    )
    status = (
        "pass"
        if all(row["status"] == "pass" for row in checks[start:])
        else "fail"
    )
    return {
        "status": status,
        "allowed_different_files": list(GENERATED_RUNTIME_EVIDENCE_FILES),
        "prerequisites": runtime_prerequisites,
        "files": files,
    }


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
    source_bindings_exact = add(
        checks,
        "source_bindings",
        ubuntu["source_bindings"],
        wsl["source_bindings"],
    )

    png_differences: dict[str, Any] = {}
    normalized_comparisons: dict[str, Any] = {}
    runtime_hash_comparisons: dict[str, Any] = {}
    for study in EXPECTED_STUDIES:
        left = ubuntu["study_evidence"][study]
        right = wsl["study_evidence"][study]
        exact_results: dict[str, bool] = {}
        for key in (
            "verification_category",
            "python_reported_fields",
            "r_metrics",
            "verification_status",
            "v4_documented_not_equal_fields",
            "reviewer_packet_membership",
            "reviewer_packet_file_count",
            "apa_runtime_binding_sha256",
            "matched_limitation_runtime_sha256",
        ):
            exact_results[key] = add(
                checks,
                f"{study}.{key}",
                left[key],
                right[key],
            )
        figure_semantics_exact = add(
            checks,
            f"{study}.figure_semantics",
            left["figures"]["manifest_semantics"],
            right["figures"]["manifest_semantics"],
        )
        normalized = compare_verification_comparisons(
            checks,
            study,
            left["verification_comparisons"],
            right["verification_comparisons"],
        )
        normalized_comparisons[study] = normalized

        prerequisites = {
            "source_bindings_exact": source_bindings_exact,
            "verification_category_exact": exact_results["verification_category"],
            "python_reported_fields_exact": exact_results[
                "python_reported_fields"
            ],
            "r_metrics_exact": exact_results["r_metrics"],
            "verification_status_exact": exact_results["verification_status"],
            "verification_status_pass": left["verification_status"]
            == right["verification_status"]
            == "pass",
            "verification_comparisons_normalized": normalized["status"] == "pass",
            "v4_documented_not_equal_fields_exact": exact_results[
                "v4_documented_not_equal_fields"
            ],
            "reviewer_packet_membership_exact": exact_results[
                "reviewer_packet_membership"
            ],
            "reviewer_packet_file_count_exact": exact_results[
                "reviewer_packet_file_count"
            ],
            "apa_runtime_binding_exact": exact_results[
                "apa_runtime_binding_sha256"
            ],
            "matched_limitation_exact": exact_results[
                "matched_limitation_runtime_sha256"
            ],
            "figure_semantics_exact": figure_semantics_exact,
        }
        runtime_hash_comparisons[study] = compare_reviewer_packet_hashes(
            checks,
            study,
            left["reviewer_packet_source_hashes"],
            right["reviewer_packet_source_hashes"],
            prerequisites,
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
        "verification_comparison_normalization": {
            "canonical_fields_required_exact": list(COMPARISON_CANONICAL_FIELDS),
            "both_statuses_required": "pass",
            "absolute_difference_serialization_tolerance": (
                ABSOLUTE_DIFFERENCE_SERIALIZATION_TOLERANCE_TEXT
            ),
            "studies": normalized_comparisons,
        },
        "generated_runtime_evidence_hash_comparison": {
            "allowed_different_files": list(GENERATED_RUNTIME_EVIDENCE_FILES),
            "immutable_or_canonical_packet_hashes_required_exact": True,
            "studies": runtime_hash_comparisons,
        },
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
        "status": (
            "technical_release_ready_not_authorized"
            if ready
            else "cross_platform_comparison_failed"
        ),
    }
    write(args.readiness, readiness)
    if failed:
        raise SystemExit("cross-platform proof mismatch:\n" + "\n".join(failed))
    print(
        "PYSTATSV1_PSYCH_DESIGN_CROSS_PLATFORM_COMPARISON_OK "
        f"checks={len(checks)} png_byte_identity_required=false "
        "runtime_evidence_hash_differences=policy_governed"
    )


if __name__ == "__main__":
    main()
