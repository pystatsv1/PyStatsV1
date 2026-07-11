#!/usr/bin/env python3
"""Reusable Book 1 design-contract audit library.

The library separates five questions that must not be collapsed:

* semantic design and data-layout validity;
* exact release-fingerprint identity;
* analysis-binding alignment;
* figure-binding alignment; and
* reporting-binding alignment.

The implementation is intentionally standard-library only so the structural
contract can be audited before the numerical companion dependencies are
installed.  Public callers normally use :func:`audit_companion` and
:func:`write_audit_outputs`.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT_NAME = "BOOK1_DESIGN_CONTRACT.json"
RECEIPT_SCHEMA_VERSION = "book1-design-audit-receipt-v0.1"
PASS = "PASS"
FAIL = "FAIL"
NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_KEYS = (
    "semantic_design_status",
    "release_fingerprint_status",
    "analysis_binding_status",
    "figure_binding_status",
    "reporting_binding_status",
)

SEMANTIC_CATEGORY = "semantic_design"
RELEASE_CATEGORY = "release_fingerprint"
ANALYSIS_CATEGORY = "analysis_binding"
FIGURE_CATEGORY = "figure_binding"
REPORTING_CATEGORY = "reporting_binding"

CATEGORY_TO_STATUS = {
    SEMANTIC_CATEGORY: "semantic_design_status",
    RELEASE_CATEGORY: "release_fingerprint_status",
    ANALYSIS_CATEGORY: "analysis_binding_status",
    FIGURE_CATEGORY: "figure_binding_status",
    REPORTING_CATEGORY: "reporting_binding_status",
}


class ContractError(RuntimeError):
    """Raised when the machine-readable contract itself is unusable."""


@dataclass(frozen=True)
class AuditFailure:
    """One deterministic, structured audit failure."""

    category: str
    code: str
    scope: str
    message: str
    details: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "code": self.code,
            "scope": self.scope,
            "message": self.message,
            "details": _json_safe(dict(self.details)),
        }


@dataclass
class CsvProfile:
    """Parsed CSV data and deterministic structural observations."""

    path: str
    source_sha256: str | None
    byte_count: int | None
    utf8_valid: bool
    header: list[str]
    rows: list[list[str]]
    row_width_mismatch_count: int
    duplicate_columns: list[str]
    exact_duplicate_row_count: int
    missing_value_counts: dict[str, int]
    whitespace_counts: dict[str, int]
    numeric_profiles: dict[str, dict[str, Any]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def records(self) -> list[dict[str, str]]:
        """Return row dictionaries when the header is usable.

        Duplicate column names make a dictionary representation ambiguous, so
        callers receive an empty list in that case.  Short rows are padded with
        empty strings; long rows retain only declared header positions because
        the width defect is already reported separately.
        """

        if not self.header or self.duplicate_columns:
            return []
        result: list[dict[str, str]] = []
        for row in self.rows:
            padded = list(row[: len(self.header)])
            if len(padded) < len(self.header):
                padded.extend([""] * (len(self.header) - len(padded)))
            result.append(dict(zip(self.header, padded)))
        return result


class FailureCollector:
    """Collect failures without duplicating identical records."""

    def __init__(self, allowed_codes: Sequence[str]) -> None:
        self.allowed_codes = set(allowed_codes)
        self._rows: list[AuditFailure] = []
        self._keys: set[tuple[str, str, str, str, str]] = set()

    def add(
        self,
        category: str,
        code: str,
        scope: str,
        message: str,
        **details: Any,
    ) -> None:
        if category not in CATEGORY_TO_STATUS:
            raise ContractError(f"unknown failure category: {category}")
        if code not in self.allowed_codes:
            raise ContractError(f"failure code is not declared by the contract: {code}")
        normalized = _json_safe(details)
        details_key = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
        key = (category, code, scope, message, details_key)
        if key in self._keys:
            return
        self._keys.add(key)
        self._rows.append(
            AuditFailure(
                category=category,
                code=code,
                scope=scope,
                message=message,
                details=normalized,
            )
        )

    def rows(self) -> list[AuditFailure]:
        return sorted(
            self._rows,
            key=lambda row: (
                row.category,
                row.scope,
                row.code,
                row.message,
                json.dumps(row.details, ensure_ascii=False, sort_keys=True),
            ),
        )

    def for_scope(self, scope: str) -> list[AuditFailure]:
        prefix = f"{scope}."
        return [
            row
            for row in self.rows()
            if row.scope == scope or row.scope.startswith(prefix)
        ]

    def has_category(self, category: str, *, scope: str | None = None) -> bool:
        for row in self._rows:
            if row.category != category:
                continue
            if scope is None:
                return True
            if row.scope == scope or row.scope.startswith(f"{scope}."):
                return True
        return False


# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, set):
        return [_json_safe(item) for item in sorted(value, key=str)]
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "+Infinity" if value > 0 else "-Infinity"
    return value


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON bytes with one trailing newline."""

    return (
        json.dumps(
            _json_safe(dict(payload)),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(parts: Iterable[str]) -> str:
    return sha256_bytes("\n".join(parts).encode("utf-8"))


def _safe_relative_path(root: Path, relative: str, *, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or not relative or ".." in candidate.parts:
        raise ContractError(f"unsafe {label} path in contract: {relative!r}")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ContractError(f"{label} escapes companion root: {relative!r}") from exc
    return resolved


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"unable to read {label}: {path}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"{label} must contain a JSON object: {path}")
    return payload


def load_contract(
    root: Path | str = ROOT,
    contract_path: Path | str | None = None,
) -> tuple[dict[str, Any], Path, str]:
    """Load and minimally validate the versioned design contract."""

    root_path = Path(root).resolve()
    path = (
        Path(contract_path).resolve()
        if contract_path is not None
        else root_path / DEFAULT_CONTRACT_NAME
    )
    if not path.is_file():
        raise ContractError(f"missing design contract: {path}")
    payload = _load_json_object(path, label="design contract")

    required_top_level = {
        "schema_version",
        "companion_version",
        "required_pystatsv1_release",
        "synthetic_data_only",
        "framework",
        "status_semantics",
        "global_rules",
        "failure_codes",
        "chapters",
        "cross_companion_rules",
        "figure_bindings",
        "reporting_bindings",
        "historical_preservation",
        "receipt_contract",
    }
    missing = sorted(required_top_level - set(payload))
    if missing:
        raise ContractError(f"design contract is missing top-level keys: {missing}")
    if payload.get("schema_version") != "book1-design-contract-v0.1":
        raise ContractError("unsupported Book 1 design-contract schema")
    if payload.get("synthetic_data_only") is not True:
        raise ContractError("design contract must declare synthetic_data_only=true")
    chapters = payload.get("chapters")
    if not isinstance(chapters, dict) or not chapters:
        raise ContractError("design contract must declare chapter objects")
    codes = payload.get("failure_codes")
    if not isinstance(codes, list) or not codes or len(codes) != len(set(codes)):
        raise ContractError("design contract failure_codes must be a unique nonempty list")
    receipt = payload.get("receipt_contract")
    if not isinstance(receipt, dict):
        raise ContractError("design contract receipt_contract must be an object")
    if receipt.get("deterministic") is not True:
        raise ContractError("design audit receipt must be deterministic")
    if receipt.get("wall_clock_timestamp_prohibited") is not True:
        raise ContractError("design audit receipt must prohibit wall-clock timestamps")
    if receipt.get("required_top_level_statuses") != list(STATUS_KEYS):
        raise ContractError("design audit receipt status contract changed unexpectedly")
    return payload, path, sha256_file(path)


# ---------------------------------------------------------------------------
# CSV profiling and semantic design checks
# ---------------------------------------------------------------------------


def _read_csv_profile(
    path: Path,
    relative_path: str,
    chapter: Mapping[str, Any],
    collector: FailureCollector,
    scope: str,
) -> CsvProfile:
    numeric_contract = (
        chapter.get("semantic_contract", {}).get("numeric_fields", {})
    )
    required_columns = (
        chapter.get("semantic_contract", {})
        .get("columns", {})
        .get("required", [])
    )

    if not path.is_file():
        collector.add(
            SEMANTIC_CATEGORY,
            "MISSING_REQUIRED_COLUMN",
            scope,
            "The declared source CSV is missing.",
            path=relative_path,
        )
        collector.add(
            RELEASE_CATEGORY,
            "SOURCE_FINGERPRINT_MISMATCH",
            scope,
            "The exact approved source fingerprint cannot be verified because the CSV is missing.",
            path=relative_path,
        )
        return CsvProfile(
            path=relative_path,
            source_sha256=None,
            byte_count=None,
            utf8_valid=False,
            header=[],
            rows=[],
            row_width_mismatch_count=0,
            duplicate_columns=[],
            exact_duplicate_row_count=0,
            missing_value_counts={str(name): 0 for name in required_columns},
            whitespace_counts={str(name): 0 for name in required_columns},
            numeric_profiles={},
        )

    data = path.read_bytes()
    source_hash = sha256_bytes(data)
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        collector.add(
            SEMANTIC_CATEGORY,
            "CSV_NOT_UTF8",
            scope,
            "The declared source CSV is not valid UTF-8.",
            path=relative_path,
        )
        collector.add(
            RELEASE_CATEGORY,
            "SOURCE_FINGERPRINT_MISMATCH",
            scope,
            "The source bytes do not match the approved release fingerprint.",
            path=relative_path,
            actual_sha256=source_hash,
        )
        return CsvProfile(
            path=relative_path,
            source_sha256=source_hash,
            byte_count=len(data),
            utf8_valid=False,
            header=[],
            rows=[],
            row_width_mismatch_count=0,
            duplicate_columns=[],
            exact_duplicate_row_count=0,
            missing_value_counts={str(name): 0 for name in required_columns},
            whitespace_counts={str(name): 0 for name in required_columns},
            numeric_profiles={},
        )

    try:
        parsed = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error as exc:
        collector.add(
            SEMANTIC_CATEGORY,
            "MISSING_REQUIRED_VALUE",
            scope,
            "The source CSV could not be parsed consistently.",
            path=relative_path,
            parser_error=str(exc),
        )
        parsed = []

    header = list(parsed[0]) if parsed else []
    rows = [list(row) for row in parsed[1:]] if parsed else []
    duplicates = sorted(
        name for name, count in Counter(header).items() if count > 1
    )
    if duplicates:
        collector.add(
            SEMANTIC_CATEGORY,
            "DUPLICATE_COLUMN_NAME",
            scope,
            "The CSV header contains duplicate column names.",
            duplicate_columns=duplicates,
        )

    expected = [str(name) for name in required_columns]
    missing_columns = [name for name in expected if name not in header]
    unexpected_columns = [name for name in header if name not in expected]
    if missing_columns:
        collector.add(
            SEMANTIC_CATEGORY,
            "MISSING_REQUIRED_COLUMN",
            scope,
            "The CSV is missing one or more required columns.",
            missing_columns=missing_columns,
            expected_columns=expected,
            observed_columns=header,
        )
    if unexpected_columns:
        collector.add(
            SEMANTIC_CATEGORY,
            "UNEXPECTED_COLUMN",
            scope,
            "The CSV contains one or more unexpected columns.",
            unexpected_columns=unexpected_columns,
            expected_columns=expected,
            observed_columns=header,
        )
    if not missing_columns and not unexpected_columns and header != expected:
        collector.add(
            SEMANTIC_CATEGORY,
            "COLUMN_ORDER_MISMATCH",
            scope,
            "The CSV column order does not match the declared contract.",
            expected_columns=expected,
            observed_columns=header,
        )

    short_rows = sum(len(row) < len(header) for row in rows)
    long_rows = sum(len(row) > len(header) for row in rows)
    if short_rows:
        collector.add(
            SEMANTIC_CATEGORY,
            "MISSING_REQUIRED_VALUE",
            scope,
            "One or more CSV rows contain fewer values than the header.",
            short_row_count=short_rows,
        )
    if long_rows:
        collector.add(
            SEMANTIC_CATEGORY,
            "UNEXPECTED_COLUMN",
            scope,
            "One or more CSV rows contain more values than the header.",
            long_row_count=long_rows,
        )

    row_counter = Counter(tuple(row) for row in rows)
    duplicate_extra = sum(count - 1 for count in row_counter.values() if count > 1)
    if duplicate_extra:
        collector.add(
            SEMANTIC_CATEGORY,
            "EXACT_DUPLICATE_ROW",
            scope,
            "The CSV contains exact duplicate data rows.",
            duplicate_extra_row_count=duplicate_extra,
        )

    missing_counts = {name: 0 for name in expected}
    whitespace_counts = {name: 0 for name in expected}
    numeric_values: dict[str, list[float]] = {
        str(name): [] for name in numeric_contract
    }
    nonnumeric_examples: dict[str, list[str]] = defaultdict(list)
    nonfinite_examples: dict[str, list[str]] = defaultdict(list)

    usable_records: list[dict[str, str]] = []
    if header and not duplicates:
        for row in rows:
            padded = list(row[: len(header)])
            if len(padded) < len(header):
                padded.extend([""] * (len(header) - len(padded)))
            usable_records.append(dict(zip(header, padded)))

    identifier_column = (
        chapter.get("semantic_contract", {})
        .get("identifier", {})
        .get("column")
    )

    for record in usable_records:
        for name in expected:
            if name not in record:
                continue
            raw = record[name]
            if raw == "":
                missing_counts[name] += 1
            if raw != raw.strip():
                whitespace_counts[name] += 1
        for name in numeric_contract:
            if name not in record:
                continue
            raw = record[name]
            if raw == "":
                continue
            try:
                value = float(raw)
            except ValueError:
                if len(nonnumeric_examples[name]) < 5:
                    nonnumeric_examples[name].append(raw)
                continue
            if not math.isfinite(value):
                if len(nonfinite_examples[name]) < 5:
                    nonfinite_examples[name].append(raw)
                continue
            numeric_values[name].append(value)

    for name, count in sorted(missing_counts.items()):
        if count:
            collector.add(
                SEMANTIC_CATEGORY,
                "MISSING_REQUIRED_VALUE",
                scope,
                "A required column contains missing values.",
                column=name,
                missing_count=count,
            )
            if name == identifier_column:
                collector.add(
                    SEMANTIC_CATEGORY,
                    "EMPTY_IDENTIFIER",
                    scope,
                    "The participant identifier column contains empty values.",
                    column=name,
                    empty_count=count,
                )

    for name, count in sorted(whitespace_counts.items()):
        if count:
            collector.add(
                SEMANTIC_CATEGORY,
                "LEADING_OR_TRAILING_WHITESPACE",
                scope,
                "A required field contains leading or trailing whitespace.",
                column=name,
                affected_row_count=count,
            )

    for name in sorted(numeric_contract):
        if nonnumeric_examples[name]:
            collector.add(
                SEMANTIC_CATEGORY,
                "NONNUMERIC_REQUIRED_VALUE",
                scope,
                "A required numeric field contains nonnumeric values.",
                column=name,
                examples=nonnumeric_examples[name],
            )
        if nonfinite_examples[name]:
            collector.add(
                SEMANTIC_CATEGORY,
                "NONFINITE_NUMERIC_VALUE",
                scope,
                "A required numeric field contains NaN or an infinite value.",
                column=name,
                examples=nonfinite_examples[name],
            )

    numeric_profiles: dict[str, dict[str, Any]] = {}
    for name in sorted(numeric_contract):
        values = numeric_values[name]
        numeric_profiles[name] = {
            "parseable_finite_count": len(values),
            "distinct_finite_values": len(set(values)),
            "observed_min": min(values) if values else None,
            "observed_max": max(values) if values else None,
            "nonnumeric_count": len(
                [
                    record.get(name, "")
                    for record in usable_records
                    if record.get(name, "")
                    and not _is_numeric(record.get(name, ""))
                ]
            ),
            "nonfinite_count": len(
                [
                    record.get(name, "")
                    for record in usable_records
                    if _is_nonfinite_numeric(record.get(name, ""))
                ]
            ),
        }

    return CsvProfile(
        path=relative_path,
        source_sha256=source_hash,
        byte_count=len(data),
        utf8_valid=True,
        header=header,
        rows=rows,
        row_width_mismatch_count=short_rows + long_rows,
        duplicate_columns=duplicates,
        exact_duplicate_row_count=duplicate_extra,
        missing_value_counts=missing_counts,
        whitespace_counts=whitespace_counts,
        numeric_profiles=numeric_profiles,
    )


def _is_numeric(raw: str) -> bool:
    try:
        float(raw)
    except (TypeError, ValueError):
        return False
    return True


def _is_nonfinite_numeric(raw: str) -> bool:
    if not raw:
        return False
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return False
    return not math.isfinite(value)


def _values(records: Sequence[Mapping[str, str]], name: str) -> list[str]:
    return [str(record.get(name, "")) for record in records]


def _nonblank_values(records: Sequence[Mapping[str, str]], name: str) -> list[str]:
    return [value for value in _values(records, name) if value != ""]


def _identifier_summary(
    records: Sequence[Mapping[str, str]],
    identifier_column: str,
) -> dict[str, Any]:
    values = _nonblank_values(records, identifier_column)
    counts = Counter(values)
    return {
        "column": identifier_column,
        "nonblank_value_count": len(values),
        "unique_value_count": len(counts),
        "frequency_distribution": {
            str(frequency): count
            for frequency, count in sorted(Counter(counts.values()).items())
        },
        "duplicate_extra_row_count": sum(
            count - 1 for count in counts.values() if count > 1
        ),
    }


def _check_factor_levels(
    records: Sequence[Mapping[str, str]],
    factors: Mapping[str, Any],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    profiles: dict[str, Any] = {}
    for name, factor_contract in sorted(factors.items()):
        expected = [str(value) for value in factor_contract.get("exact_levels", [])]
        observed_values = [
            str(record.get(name, ""))
            for record in records
            if str(record.get(name, "")) != ""
        ]
        counts = Counter(observed_values)
        observed = sorted(counts)
        unexpected = sorted(set(observed) - set(expected))
        missing = [value for value in expected if value not in counts]
        if unexpected:
            collector.add(
                SEMANTIC_CATEGORY,
                "UNEXPECTED_FACTOR_LEVEL",
                scope,
                "A factor contains an unexpected level.",
                factor=name,
                unexpected_levels=unexpected,
                expected_levels=expected,
            )
        if missing:
            collector.add(
                SEMANTIC_CATEGORY,
                "UNEXPECTED_FACTOR_LEVEL",
                scope,
                "A factor is missing one or more required levels.",
                factor=name,
                missing_levels=missing,
                expected_levels=expected,
            )
        profiles[name] = {
            "expected_levels": expected,
            "observed_levels": observed,
            "counts": dict(sorted(counts.items())),
            "unexpected_levels": unexpected,
            "missing_levels": missing,
        }
    return profiles


def _check_independent_design(
    chapter_id: str,
    chapter: Mapping[str, Any],
    records: Sequence[Mapping[str, str]],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    semantic = chapter["semantic_contract"]
    identifier = semantic["identifier"]
    id_column = str(identifier["column"])
    summary = _identifier_summary(records, id_column)
    ids = _nonblank_values(records, id_column)
    id_counts = Counter(ids)
    duplicates = sorted(name for name, count in id_counts.items() if count > 1)
    if identifier.get("unique_within_dataset") is True and duplicates:
        collector.add(
            SEMANTIC_CATEGORY,
            "INDEPENDENT_DESIGN_ID_NOT_UNIQUE",
            scope,
            "An independent-row design contains repeated participant identifiers.",
            identifier_column=id_column,
            duplicate_identifier_count=len(duplicates),
            duplicate_extra_row_count=sum(id_counts[name] - 1 for name in duplicates),
            examples=duplicates[:10],
        )

    factors = _check_factor_levels(
        records,
        semantic.get("factors", {}),
        collector,
        scope,
    )

    by_id: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for record in records:
        pid = str(record.get(id_column, ""))
        if pid:
            by_id[pid].append(record)

    if identifier.get("one_group_per_participant") is True:
        group_column = next(iter(semantic.get("factors", {})), "group")
        multiple = {
            pid: sorted({str(row.get(group_column, "")) for row in rows})
            for pid, rows in by_id.items()
            if len({str(row.get(group_column, "")) for row in rows}) > 1
        }
        if multiple:
            collector.add(
                SEMANTIC_CATEGORY,
                "PARTICIPANT_ASSIGNED_TO_MULTIPLE_GROUPS",
                scope,
                "A participant identifier is assigned to more than one group.",
                examples=dict(list(sorted(multiple.items()))[:10]),
            )

    if identifier.get("one_condition_per_participant") is True:
        factor_column = next(iter(semantic.get("factors", {})), "study_condition")
        multiple = {
            pid: sorted({str(row.get(factor_column, "")) for row in rows})
            for pid, rows in by_id.items()
            if len({str(row.get(factor_column, "")) for row in rows}) > 1
        }
        if multiple:
            collector.add(
                SEMANTIC_CATEGORY,
                "PARTICIPANT_ASSIGNED_TO_MULTIPLE_GROUPS",
                scope,
                "A participant identifier is assigned to more than one condition.",
                factor=factor_column,
                examples=dict(list(sorted(multiple.items()))[:10]),
            )

    cell_counts: dict[str, int] = {}
    factorial = semantic.get("factorial_structure")
    if isinstance(factorial, dict):
        factor_names = list(
            chapter.get("analysis_binding", {})
            .get("binding_details", {})
            .get("factors", list(semantic.get("factors", {})))
        )
        expected_cells = [
            tuple(values)
            for values in _cartesian_product(
                [
                    semantic["factors"][name].get("exact_levels", [])
                    for name in factor_names
                ]
            )
        ]
        observed_counter: Counter[tuple[str, ...]] = Counter()
        for record in records:
            values = tuple(str(record.get(name, "")) for name in factor_names)
            if all(values):
                observed_counter[values] += 1
        missing_cells = [cell for cell in expected_cells if observed_counter[cell] == 0]
        unexpected_cells = [
            cell for cell in sorted(observed_counter) if cell not in set(expected_cells)
        ]
        if missing_cells:
            collector.add(
                SEMANTIC_CATEGORY,
                "MISSING_FACTOR_CELL",
                scope,
                "The factorial table is missing one or more required cells.",
                factor_order=factor_names,
                missing_cells=["|".join(cell) for cell in missing_cells],
            )
        if unexpected_cells:
            collector.add(
                SEMANTIC_CATEGORY,
                "UNEXPECTED_FACTOR_CELL",
                scope,
                "The factorial table contains one or more unexpected cells.",
                factor_order=factor_names,
                unexpected_cells=["|".join(cell) for cell in unexpected_cells],
            )
        if factorial.get("expected_cell_count") != len(observed_counter):
            if not missing_cells and not unexpected_cells:
                collector.add(
                    SEMANTIC_CATEGORY,
                    "MISSING_FACTOR_CELL",
                    scope,
                    "The observed factorial cell count does not match the contract.",
                    expected_cell_count=factorial.get("expected_cell_count"),
                    observed_cell_count=len(observed_counter),
                )
        cell_counts = {
            "|".join(cell): count
            for cell, count in sorted(observed_counter.items())
        }

        if identifier.get("one_factor_cell_per_participant") is True:
            multiple_cells: dict[str, list[str]] = {}
            for pid, rows in by_id.items():
                cells = sorted(
                    {
                        "|".join(str(row.get(name, "")) for name in factor_names)
                        for row in rows
                    }
                )
                if len(cells) > 1:
                    multiple_cells[pid] = cells
            if multiple_cells:
                collector.add(
                    SEMANTIC_CATEGORY,
                    "PARTICIPANT_ASSIGNED_TO_MULTIPLE_FACTOR_CELLS",
                    scope,
                    "A participant identifier is assigned to multiple factorial cells.",
                    examples=dict(list(sorted(multiple_cells.items()))[:10]),
                )

    exact_sequence = identifier.get("required_exact_sequence")
    if isinstance(exact_sequence, dict) and records:
        prefix = str(exact_sequence["prefix"])
        start = int(exact_sequence["start"])
        end = int(exact_sequence["end"])
        width = int(exact_sequence["zero_pad_width"])
        expected_ids = [f"{prefix}{value:0{width}d}" for value in range(start, end + 1)]
        observed_ids = _values(records, id_column)
        if observed_ids != expected_ids:
            collector.add(
                SEMANTIC_CATEGORY,
                "MISSING_REQUIRED_VALUE",
                scope,
                "The required participant-identifier sequence is incomplete, unexpected, or out of order.",
                identifier_column=id_column,
                expected_first=expected_ids[:3],
                expected_last=expected_ids[-3:],
                observed_first=observed_ids[:3],
                observed_last=observed_ids[-3:],
                expected_count=len(expected_ids),
                observed_count=len(observed_ids),
            )

    summary["factor_profiles"] = factors
    summary["factor_cell_counts"] = cell_counts
    return summary


def _check_paired_design(
    chapter: Mapping[str, Any],
    records: Sequence[Mapping[str, str]],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    semantic = chapter["semantic_contract"]
    identifier = semantic["identifier"]
    id_column = str(identifier["column"])
    summary = _identifier_summary(records, id_column)
    counts = Counter(_nonblank_values(records, id_column))
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        collector.add(
            SEMANTIC_CATEGORY,
            "PAIRED_DESIGN_ID_NOT_UNIQUE",
            scope,
            "The paired-wide design contains repeated participant identifiers.",
            examples=duplicates[:10],
            duplicate_extra_row_count=sum(counts[name] - 1 for name in duplicates),
        )

    pairing = semantic.get("pairing", {})
    required_pair_columns = [str(name) for name in pairing.get("required_columns", [])]
    incomplete_rows = 0
    for record in records:
        if any(str(record.get(name, "")) == "" for name in required_pair_columns):
            incomplete_rows += 1
    if incomplete_rows:
        collector.add(
            SEMANTIC_CATEGORY,
            "INCOMPLETE_PAIRED_ROW",
            scope,
            "One or more paired rows do not contain both required measurements.",
            required_pair_columns=required_pair_columns,
            incomplete_row_count=incomplete_rows,
        )
    summary["required_pair_columns"] = required_pair_columns
    summary["incomplete_pair_row_count"] = incomplete_rows
    return summary


def _check_repeated_design(
    chapter: Mapping[str, Any],
    records: Sequence[Mapping[str, str]],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    semantic = chapter["semantic_contract"]
    identifier = semantic["identifier"]
    id_column = str(identifier["column"])
    occasion_contract = semantic["occasions"]
    occasion_column = str(occasion_contract["column"])
    expected_occasions = [str(value) for value in occasion_contract["exact_levels"]]
    summary = _identifier_summary(records, id_column)

    key_counts: Counter[tuple[str, str]] = Counter()
    by_id: dict[str, list[str]] = defaultdict(list)
    occasion_counts: Counter[str] = Counter()
    for record in records:
        pid = str(record.get(id_column, ""))
        occasion = str(record.get(occasion_column, ""))
        if pid and occasion:
            key_counts[(pid, occasion)] += 1
            by_id[pid].append(occasion)
            occasion_counts[occasion] += 1

    duplicate_keys = sorted(
        f"{pid}|{occasion}"
        for (pid, occasion), count in key_counts.items()
        if count > 1
    )
    if duplicate_keys:
        collector.add(
            SEMANTIC_CATEGORY,
            "DUPLICATE_SUBJECT_OCCASION",
            scope,
            "A participant/occasion composite key appears more than once.",
            examples=duplicate_keys[:10],
            duplicate_extra_row_count=sum(
                count - 1 for count in key_counts.values() if count > 1
            ),
        )

    observed_occasions = sorted(occasion_counts)
    unexpected = sorted(set(observed_occasions) - set(expected_occasions))
    if unexpected:
        collector.add(
            SEMANTIC_CATEGORY,
            "UNEXPECTED_OCCASION",
            scope,
            "The repeated-measures table contains an unexpected occasion.",
            unexpected_occasions=unexpected,
            expected_occasions=expected_occasions,
        )

    incomplete: dict[str, dict[str, int]] = {}
    for pid, occasions in sorted(by_id.items()):
        counts = Counter(occasions)
        if any(counts.get(name, 0) != 1 for name in expected_occasions) or any(
            name not in expected_occasions for name in counts
        ):
            incomplete[pid] = dict(sorted(counts.items()))
        expected_rows = identifier.get("expected_rows_per_participant")
        if expected_rows is not None and len(occasions) != int(expected_rows):
            incomplete[pid] = dict(sorted(counts.items()))
    if incomplete:
        collector.add(
            SEMANTIC_CATEGORY,
            "INCOMPLETE_REPEATED_TRAJECTORY",
            scope,
            "One or more participants do not have exactly one row at every required occasion.",
            expected_occasions=expected_occasions,
            affected_participant_count=len(incomplete),
            examples=dict(list(incomplete.items())[:10]),
        )

    cartesian = semantic.get("cartesian_structure", {})
    expected_long_rows = cartesian.get("expected_long_rows")
    if expected_long_rows is not None and len(records) != int(expected_long_rows):
        collector.add(
            SEMANTIC_CATEGORY,
            "REPEATED_MEASURES_ROW_COUNT_MISMATCH",
            scope,
            "The repeated-measures long table does not have the declared row count.",
            expected_row_count=int(expected_long_rows),
            observed_row_count=len(records),
        )

    observed_wide_shape = [len(by_id), len(expected_occasions)]
    expected_wide_shape = cartesian.get("expected_wide_shape")
    complete_keys = not duplicate_keys and not incomplete and not unexpected
    if expected_wide_shape is not None and (
        observed_wide_shape != list(expected_wide_shape) or not complete_keys
    ):
        collector.add(
            SEMANTIC_CATEGORY,
            "PIVOT_SHAPE_MISMATCH",
            scope,
            "The long table cannot produce the declared complete wide repeated-measures shape.",
            expected_wide_shape=list(expected_wide_shape),
            observed_wide_shape=observed_wide_shape,
            complete_subject_occasion_keys=complete_keys,
        )

    summary.update(
        {
            "occasion_column": occasion_column,
            "expected_occasions": expected_occasions,
            "observed_occasion_counts": dict(sorted(occasion_counts.items())),
            "duplicate_subject_occasion_keys": duplicate_keys,
            "complete_trajectory_count": len(by_id) - len(incomplete),
            "incomplete_trajectory_count": len(incomplete),
            "observed_wide_shape": observed_wide_shape,
        }
    )
    return summary


def _check_observational_pair_design(
    chapter: Mapping[str, Any],
    records: Sequence[Mapping[str, str]],
    numeric_profiles: Mapping[str, Mapping[str, Any]],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    semantic = chapter["semantic_contract"]
    identifier = semantic["identifier"]
    id_column = str(identifier["column"])
    summary = _identifier_summary(records, id_column)
    counts = Counter(_nonblank_values(records, id_column))
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        collector.add(
            SEMANTIC_CATEGORY,
            "INDEPENDENT_DESIGN_ID_NOT_UNIQUE",
            scope,
            "A one-observation-per-participant table contains repeated participant identifiers.",
            examples=duplicates[:10],
            duplicate_extra_row_count=sum(counts[name] - 1 for name in duplicates),
        )

    for name, numeric_contract in sorted(semantic.get("numeric_fields", {}).items()):
        profile = numeric_profiles.get(name, {})
        distinct = int(profile.get("distinct_finite_values", 0) or 0)
        if numeric_contract.get("variance_greater_than_zero") is True and distinct <= 1:
            code = "CONSTANT_PREDICTOR" if (
                semantic.get("pairing", {}).get("predictor") == name
            ) else "CONSTANT_VARIABLE"
            collector.add(
                SEMANTIC_CATEGORY,
                code,
                scope,
                "A required variable has no observed finite variation.",
                column=name,
                distinct_finite_values=distinct,
            )
        minimum_distinct = numeric_contract.get("minimum_distinct_values")
        if minimum_distinct is not None and distinct < int(minimum_distinct):
            collector.add(
                SEMANTIC_CATEGORY,
                "INSUFFICIENT_DISTINCT_PREDICTOR_VALUES",
                scope,
                "The predictor has fewer distinct finite values than the contract requires.",
                column=name,
                minimum_distinct_values=int(minimum_distinct),
                observed_distinct_values=distinct,
            )

    pairing = semantic.get("pairing", {})
    if "variables" in pairing:
        pair_columns = [str(name) for name in pairing["variables"]]
    else:
        pair_columns = [
            str(pairing.get("predictor", "")),
            str(pairing.get("outcome", "")),
        ]
    complete_pairs = sum(
        all(str(record.get(name, "")) != "" for name in pair_columns)
        for record in records
    )
    summary["pair_columns"] = pair_columns
    summary["complete_pair_count"] = complete_pairs
    return summary


def _cartesian_product(levels: Sequence[Sequence[Any]]) -> list[list[Any]]:
    result: list[list[Any]] = [[]]
    for values in levels:
        result = [prefix + [value] for prefix in result for value in values]
    return result


# ---------------------------------------------------------------------------
# Exact release fingerprints
# ---------------------------------------------------------------------------


def _check_release_fingerprint(
    chapter_id: str,
    chapter: Mapping[str, Any],
    profile: CsvProfile,
    records: Sequence[Mapping[str, str]],
    semantic_summary: Mapping[str, Any],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    expected = chapter["release_fingerprint"]
    checks: dict[str, Any] = {}

    expected_hash = str(expected["source_csv_sha256"])
    hash_match = profile.source_sha256 == expected_hash
    checks["source_csv_sha256"] = {
        "expected": expected_hash,
        "actual": profile.source_sha256,
        "match": hash_match,
    }
    if not hash_match:
        collector.add(
            RELEASE_CATEGORY,
            "SOURCE_FINGERPRINT_MISMATCH",
            scope,
            "The source CSV does not match the exact approved release fingerprint.",
            expected_sha256=expected_hash,
            actual_sha256=profile.source_sha256,
        )

    expected_rows = int(expected["row_count"])
    row_match = profile.row_count == expected_rows
    checks["row_count"] = {
        "expected": expected_rows,
        "actual": profile.row_count,
        "match": row_match,
    }
    if not row_match:
        collector.add(
            RELEASE_CATEGORY,
            "RELEASE_ROW_COUNT_MISMATCH",
            scope,
            "The source row count does not match the approved release snapshot.",
            expected_row_count=expected_rows,
            observed_row_count=profile.row_count,
        )

    expected_unique = expected.get("unique_participant_id_count")
    if expected_unique is not None:
        observed_unique = semantic_summary.get("unique_value_count")
        checks["unique_participant_id_count"] = {
            "expected": int(expected_unique),
            "actual": observed_unique,
            "match": observed_unique == int(expected_unique),
        }

    count_contracts = (
        ("group_counts", "RELEASE_GROUP_COUNT_MISMATCH", "group"),
        ("condition_counts", "RELEASE_GROUP_COUNT_MISMATCH", "condition"),
        ("occasion_counts", "RELEASE_GROUP_COUNT_MISMATCH", "occasion"),
        ("cell_counts", "RELEASE_CELL_COUNT_MISMATCH", "cell"),
    )
    for key, code, label in count_contracts:
        if key not in expected:
            continue
        if key == "cell_counts":
            actual_counts = semantic_summary.get("factor_cell_counts", {})
        elif key == "occasion_counts":
            actual_counts = semantic_summary.get("observed_occasion_counts", {})
        else:
            if key == "group_counts":
                column = "group"
            else:
                column = "study_condition"
            actual_counts = dict(
                sorted(
                    Counter(
                        str(record.get(column, ""))
                        for record in records
                        if str(record.get(column, "")) != ""
                    ).items()
                )
            )
        expected_counts = {
            str(name): int(value) for name, value in expected[key].items()
        }
        match = actual_counts == expected_counts
        checks[key] = {
            "expected": expected_counts,
            "actual": actual_counts,
            "match": match,
        }
        if not match:
            collector.add(
                RELEASE_CATEGORY,
                code,
                scope,
                f"The approved release {label} counts do not match.",
                metric=key,
                expected=expected_counts,
                actual=actual_counts,
            )

    ranges = expected.get("observed_numeric_ranges", {})
    range_checks: dict[str, Any] = {}
    for name, limits in sorted(ranges.items()):
        profile_row = profile.numeric_profiles.get(name, {})
        actual = {
            "min": profile_row.get("observed_min"),
            "max": profile_row.get("observed_max"),
        }
        expected_limits = {
            "min": limits.get("min"),
            "max": limits.get("max"),
        }
        range_checks[name] = {
            "expected": expected_limits,
            "actual": actual,
            "match": actual == expected_limits,
        }
    if range_checks:
        checks["observed_numeric_ranges"] = range_checks

    pairing_contract = expected.get("pairing_fingerprints")
    if isinstance(pairing_contract, dict):
        ids = _values(records, "participant_id")
        x_values = _values(records, "study_hours")
        y_values = _values(records, "test_score")
        actual_pairing = {
            "study_hours_sequence_sha256": sha256_text(x_values),
            "test_score_sequence_sha256": sha256_text(y_values),
            "ordered_id_predictor_outcome_sha256": sha256_text(
                f"{pid}\0{x}\0{y}"
                for pid, x, y in zip(ids, x_values, y_values)
            ),
            "ordered_predictor_outcome_sha256": sha256_text(
                f"{x}\0{y}" for x, y in zip(x_values, y_values)
            ),
            "unordered_predictor_outcome_multiset_sha256": sha256_text(
                sorted(f"{x}\0{y}" for x, y in zip(x_values, y_values))
            ),
        }
        pairing_checks: dict[str, Any] = {}
        mismatches: dict[str, Any] = {}
        for key, actual_value in actual_pairing.items():
            expected_value = pairing_contract.get(key)
            match = actual_value == expected_value
            pairing_checks[key] = {
                "expected": expected_value,
                "actual": actual_value,
                "match": match,
            }
            if not match:
                mismatches[key] = pairing_checks[key]
        checks["pairing_fingerprints"] = pairing_checks
        if mismatches:
            collector.add(
                RELEASE_CATEGORY,
                "PAIRING_FINGERPRINT_MISMATCH",
                scope,
                "The fixed-release predictor/outcome pairing fingerprint does not match.",
                mismatches=mismatches,
            )

    return checks


# ---------------------------------------------------------------------------
# Analysis, figure, and reporting binding checks
# ---------------------------------------------------------------------------


def _check_analysis_binding(
    root: Path,
    chapter_id: str,
    chapter: Mapping[str, Any],
    collector: FailureCollector,
    scope: str,
) -> dict[str, Any]:
    binding = chapter.get("analysis_binding")
    if not isinstance(binding, dict):
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The chapter lacks an analysis-binding object.",
        )
        return {"status": FAIL}

    observations: dict[str, Any] = {
        "data_file": binding.get("data_file"),
        "method": binding.get("method"),
        "apa_source_id": binding.get("apa_source_id"),
        "scripts": {},
        "outputs": binding.get("outputs"),
    }

    if binding.get("data_file") != chapter.get("source_csv"):
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The analysis data path does not match the chapter source path.",
            chapter_source_csv=chapter.get("source_csv"),
            analysis_data_file=binding.get("data_file"),
        )

    for language in ("python", "r"):
        row = binding.get(language)
        if not isinstance(row, dict):
            collector.add(
                ANALYSIS_CATEGORY,
                "ANALYSIS_BINDING_MISMATCH",
                scope,
                "A required language binding is missing.",
                language=language,
            )
            continue
        script_rel = row.get("script")
        expected_hash = row.get("script_sha256")
        if not isinstance(script_rel, str) or not isinstance(expected_hash, str):
            collector.add(
                ANALYSIS_CATEGORY,
                "ANALYSIS_BINDING_MISMATCH",
                scope,
                "A language binding lacks a script path or script fingerprint.",
                language=language,
            )
            continue
        try:
            script_path = _safe_relative_path(root, script_rel, label=f"{language} script")
        except ContractError as exc:
            collector.add(
                ANALYSIS_CATEGORY,
                "ANALYSIS_BINDING_MISMATCH",
                scope,
                str(exc),
                language=language,
                script=script_rel,
            )
            continue
        actual_hash = sha256_file(script_path) if script_path.is_file() else None
        match = actual_hash == expected_hash
        observations["scripts"][language] = {
            "path": script_rel,
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "match": match,
        }
        if not match:
            collector.add(
                ANALYSIS_CATEGORY,
                "ANALYSIS_BINDING_MISMATCH",
                scope,
                "An analysis script does not match its approved binding fingerprint.",
                language=language,
                script=script_rel,
                expected_sha256=expected_hash,
                actual_sha256=actual_hash,
            )
        if language == "r" and row.get("independent_implementation") is not True:
            collector.add(
                ANALYSIS_CATEGORY,
                "ANALYSIS_BINDING_MISMATCH",
                scope,
                "The R route is not declared as an independent implementation.",
            )

    expected_outputs = {
        "python_result": f"outputs/{chapter_id}/py_results.json",
        "r_result": f"outputs/{chapter_id}/r_results.json",
        "parity_receipt": f"outputs/{chapter_id}/parity_receipt.md",
    }
    if binding.get("outputs") != expected_outputs:
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The declared result or parity paths do not match the chapter route.",
            expected_outputs=expected_outputs,
            observed_outputs=binding.get("outputs"),
        )
    if binding.get("apa_source_id") != chapter_id:
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The APA source identifier does not match the chapter identifier.",
            expected_apa_source_id=chapter_id,
            observed_apa_source_id=binding.get("apa_source_id"),
        )
    if not isinstance(binding.get("method"), str) or not binding.get("method"):
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The analysis method label is missing.",
        )
    if not isinstance(binding.get("binding_details"), dict) or not binding.get(
        "binding_details"
    ):
        collector.add(
            ANALYSIS_CATEGORY,
            "ANALYSIS_BINDING_MISMATCH",
            scope,
            "The analysis binding lacks explicit variable, method, or direction details.",
        )
    observations["status"] = (
        FAIL if collector.has_category(ANALYSIS_CATEGORY, scope=scope) else PASS
    )
    return observations


def _check_figure_bindings(
    root: Path,
    contract: Mapping[str, Any],
    collector: FailureCollector,
) -> dict[str, Any]:
    scope = "figure_bindings"
    declared = contract.get("figure_bindings")
    if not isinstance(declared, dict):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The contract lacks a figure-bindings object.",
        )
        return {"status": FAIL, "figures": []}

    result: dict[str, Any] = {
        "specification_file": declared.get("specification_file"),
        "generator_script": declared.get("generator_script"),
        "expected_figure_count": declared.get("expected_figure_count"),
        "figures": [],
    }

    try:
        spec_path = _safe_relative_path(
            root, str(declared.get("specification_file", "")), label="figure specification"
        )
        generator_path = _safe_relative_path(
            root, str(declared.get("generator_script", "")), label="figure generator"
        )
    except ContractError as exc:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            str(exc),
        )
        result["status"] = FAIL
        return result

    spec_expected_hash = declared.get("specification_sha256")
    generator_expected_hash = declared.get("generator_script_sha256")
    spec_actual_hash = sha256_file(spec_path) if spec_path.is_file() else None
    generator_actual_hash = sha256_file(generator_path) if generator_path.is_file() else None
    result["specification_sha256"] = {
        "expected": spec_expected_hash,
        "actual": spec_actual_hash,
        "match": spec_actual_hash == spec_expected_hash,
    }
    result["generator_script_sha256"] = {
        "expected": generator_expected_hash,
        "actual": generator_actual_hash,
        "match": generator_actual_hash == generator_expected_hash,
    }
    if spec_actual_hash != spec_expected_hash:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification does not match its approved fingerprint.",
            expected_sha256=spec_expected_hash,
            actual_sha256=spec_actual_hash,
        )
    if generator_actual_hash != generator_expected_hash:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure generator does not match its approved fingerprint.",
            expected_sha256=generator_expected_hash,
            actual_sha256=generator_actual_hash,
        )

    if not spec_path.is_file():
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The declared figure specification is missing.",
            path=declared.get("specification_file"),
        )
        result["status"] = FAIL
        return result

    try:
        spec = _load_json_object(spec_path, label="figure specification")
    except ContractError as exc:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            str(exc),
        )
        result["status"] = FAIL
        return result

    if spec.get("companion_version") != contract.get("companion_version"):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification companion version does not match the design contract.",
            expected=contract.get("companion_version"),
            actual=spec.get("companion_version"),
        )
    if spec.get("required_pystatsv1_release") != contract.get(
        "required_pystatsv1_release"
    ):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification PyStatsV1 release does not match the design contract.",
            expected=contract.get("required_pystatsv1_release"),
            actual=spec.get("required_pystatsv1_release"),
        )
    if spec.get("generator") != declared.get("generator_script"):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification names a different generator script.",
            expected=declared.get("generator_script"),
            actual=spec.get("generator"),
        )

    spec_rows = spec.get("figures")
    if not isinstance(spec_rows, list):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification does not contain a figure list.",
        )
        spec_rows = []
    spec_by_id: dict[str, Mapping[str, Any]] = {}
    duplicate_ids: list[str] = []
    for row in spec_rows:
        if not isinstance(row, dict) or not isinstance(row.get("figure_id"), str):
            collector.add(
                FIGURE_CATEGORY,
                "FIGURE_BINDING_MISMATCH",
                scope,
                "A figure specification row lacks a figure identifier.",
            )
            continue
        figure_id = str(row["figure_id"])
        if figure_id in spec_by_id:
            duplicate_ids.append(figure_id)
        spec_by_id[figure_id] = row
    if duplicate_ids:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification contains duplicate figure identifiers.",
            duplicate_figure_ids=sorted(set(duplicate_ids)),
        )

    expected_count = int(declared.get("expected_figure_count", -1))
    if len(spec_rows) != expected_count:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure count does not match the design contract.",
            expected_figure_count=expected_count,
            observed_figure_count=len(spec_rows),
        )

    declared_rows = declared.get("figures")
    if not isinstance(declared_rows, list):
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The design contract does not contain a figure-binding list.",
        )
        declared_rows = []

    for row in declared_rows:
        if not isinstance(row, dict):
            continue
        figure_id = str(row.get("figure_id", ""))
        spec_row = spec_by_id.get(figure_id)
        figure_result = {
            "figure_id": figure_id,
            "declared_source_csv": row.get("source_csv"),
            "present_in_specification": spec_row is not None,
        }
        if spec_row is None:
            collector.add(
                FIGURE_CATEGORY,
                "FIGURE_BINDING_MISMATCH",
                f"{scope}.{figure_id}",
                "A declared figure is absent from the figure specification.",
                figure_id=figure_id,
            )
            result["figures"].append(figure_result)
            continue
        analysis_contract = spec_row.get("analysis_contract")
        if not isinstance(analysis_contract, dict):
            analysis_contract = {}
        expected_values = {
            "chapter_placement": row.get("chapter_placement"),
            "source_csv": row.get("source_csv"),
            "analysis_script": row.get("analysis_script"),
            "python_result": row.get("python_result"),
            "apa_source_id": row.get("apa_source_id"),
        }
        actual_values = {
            "chapter_placement": spec_row.get("chapter_placement"),
            "source_csv": spec_row.get("source_csv"),
            "analysis_script": analysis_contract.get("analysis_script"),
            "python_result": analysis_contract.get("python_result"),
            "apa_source_id": analysis_contract.get("apa_source_id"),
        }
        figure_result["expected"] = expected_values
        figure_result["actual"] = actual_values
        figure_result["match"] = expected_values == actual_values
        if expected_values != actual_values:
            collector.add(
                FIGURE_CATEGORY,
                "FIGURE_BINDING_MISMATCH",
                f"{scope}.{figure_id}",
                "A figure source, analysis, result, placement, or APA binding does not match.",
                expected=expected_values,
                actual=actual_values,
            )
        for path_key in ("source_csv", "analysis_script"):
            rel = expected_values[path_key]
            if isinstance(rel, str):
                try:
                    bound_path = _safe_relative_path(root, rel, label=f"figure {path_key}")
                except ContractError as exc:
                    collector.add(
                        FIGURE_CATEGORY,
                        "FIGURE_BINDING_MISMATCH",
                        f"{scope}.{figure_id}",
                        str(exc),
                    )
                else:
                    if not bound_path.is_file():
                        collector.add(
                            FIGURE_CATEGORY,
                            "FIGURE_BINDING_MISMATCH",
                            f"{scope}.{figure_id}",
                            "A figure binding points to a missing source file.",
                            field=path_key,
                            path=rel,
                        )
        result["figures"].append(figure_result)

    declared_ids = {
        str(row.get("figure_id")) for row in declared_rows if isinstance(row, dict)
    }
    unexpected_ids = sorted(set(spec_by_id) - declared_ids)
    if unexpected_ids:
        collector.add(
            FIGURE_CATEGORY,
            "FIGURE_BINDING_MISMATCH",
            scope,
            "The figure specification contains figures absent from the design contract.",
            unexpected_figure_ids=unexpected_ids,
        )

    for chapter_id, chapter in contract["chapters"].items():
        chapter_binding = chapter.get("figure_binding", {})
        status = chapter_binding.get("status")
        if status == "REQUIRED":
            figure_id = chapter_binding.get("figure_id")
            if figure_id not in declared_ids or figure_id not in spec_by_id:
                collector.add(
                    FIGURE_CATEGORY,
                    "FIGURE_BINDING_MISMATCH",
                    f"chapters.{chapter_id}",
                    "A chapter-required figure is not fully declared.",
                    figure_id=figure_id,
                )
        elif status != "NOT_APPLICABLE":
            collector.add(
                FIGURE_CATEGORY,
                "FIGURE_BINDING_MISMATCH",
                f"chapters.{chapter_id}",
                "A chapter figure binding has an unsupported status.",
                status=status,
            )

    result["status"] = FAIL if collector.has_category(FIGURE_CATEGORY) else PASS
    return result


def _expected_apa_sentence(chapter: str, fields: Mapping[str, Any]) -> str:
    """Mirror the approved, hash-bound Chapter 12 sentence formatter."""

    def format_p(value: Any) -> str:
        number = float(value)
        return "p < .001" if number < 0.001 else f"p = {number:.3f}".replace("0.", ".")

    if chapter == "ch05":
        return (
            f"Students in the structured strategy group (M = {fields['structured_mean']:.2f}, "
            f"SD = {fields['structured_sd']:.2f}) scored higher than students in the standard "
            f"group (M = {fields['standard_mean']:.2f}, SD = {fields['standard_sd']:.2f}), "
            f"Welch t({fields['degrees_of_freedom']:.2f}) = {fields['t_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, d = {fields['cohen_d']:.2f}."
        )
    if chapter == "ch06":
        return (
            f"Anxiety scores were lower after the workshop (M = {fields['post_mean']:.2f}) "
            f"than before it (M = {fields['pre_mean']:.2f}), "
            f"t({fields['degrees_of_freedom']}) = {fields['t_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, dz = {fields['cohen_dz']:.2f}."
        )
    if chapter == "ch07":
        return (
            f"Test scores differed across study conditions, "
            f"F({fields['df_between']}, {fields['df_within']}) = {fields['f_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, η² = {fields['eta_squared']:.2f}; the spaced-review "
            f"group had the highest mean (M = {fields['spaced_review_mean']:.2f})."
        )
    if chapter == "ch08":
        return (
            f"Structured strategy produced higher scores than standard strategy, "
            f"F({fields['df_effect']}, {fields['df_error']}) = {fields['strategy_f']:.2f}, "
            f"{format_p(fields['strategy_p'])}, ηp² = {fields['strategy_partial_eta_squared']:.2f}; "
            f"the strategy-by-feedback interaction was not supported, "
            f"F({fields['df_effect']}, {fields['df_error']}) = {fields['interaction_f']:.2f}, "
            f"{format_p(fields['interaction_p'])}, ηp² = "
            f"{fields['interaction_partial_eta_squared']:.3f}."
        )
    if chapter == "ch09":
        return (
            f"Confidence changed across time, F({fields['df_time']}, {fields['df_error']}) = "
            f"{fields['f_statistic']:.2f}, {format_p(fields['p_value'])}, "
            f"ηp² = {fields['partial_eta_squared']:.2f}; mean confidence rose from "
            f"{fields['baseline_mean']:.2f} at baseline to {fields['week_4_mean']:.2f} at week 4."
        )
    if chapter == "ch10":
        return (
            f"Weekly study hours were positively correlated with test score, "
            f"r({fields['degrees_of_freedom']}) = {fields['correlation_r']:.2f}, "
            f"{format_p(fields['p_value'])}, in this synthetic sample."
        )
    if chapter == "ch11":
        return (
            f"Study hours predicted test score, b = {fields['slope']:.2f}, "
            f"SE = {fields['slope_standard_error']:.2f}, "
            f"t({fields['degrees_of_freedom']}) = {fields['t_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, R² = {fields['r_squared']:.2f}."
        )
    raise KeyError(chapter)


def _check_reporting_bindings(
    root: Path,
    contract: Mapping[str, Any],
    collector: FailureCollector,
) -> dict[str, Any]:
    scope = "reporting_bindings"
    declared = contract.get("reporting_bindings")
    if not isinstance(declared, dict):
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The contract lacks a reporting-bindings object.",
        )
        return {"status": FAIL, "generated_output_check": "NOT_RUN"}

    result: dict[str, Any] = {
        "chapter12_source_map_script": declared.get("chapter12_source_map_script"),
        "chapters": declared.get("chapters"),
        "generated_source_map": declared.get("generated_source_map"),
        "generated_audit": declared.get("generated_audit"),
    }

    try:
        script_path = _safe_relative_path(
            root,
            str(declared.get("chapter12_source_map_script", "")),
            label="Chapter 12 source-map script",
        )
    except ContractError as exc:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            str(exc),
        )
        result["status"] = FAIL
        return result

    expected_script_hash = declared.get("chapter12_source_map_script_sha256")
    actual_script_hash = sha256_file(script_path) if script_path.is_file() else None
    result["script_sha256"] = {
        "expected": expected_script_hash,
        "actual": actual_script_hash,
        "match": actual_script_hash == expected_script_hash,
    }
    if actual_script_hash != expected_script_hash:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The Chapter 12 source-map script does not match its approved fingerprint.",
            expected_sha256=expected_script_hash,
            actual_sha256=actual_script_hash,
        )

    expected_chapters = list(contract["chapters"])
    if declared.get("chapters") != expected_chapters:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The reporting chapter route does not match the design contract chapters.",
            expected_chapters=expected_chapters,
            observed_chapters=declared.get("chapters"),
        )

    expected_record_bindings = [
        "chapter",
        "analysis_name",
        "python_result_file",
        "r_result_file",
        "parity_receipt",
        "python_result_source_sha256",
        "apa_result",
    ]
    if declared.get("each_record_must_bind") != expected_record_bindings:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The required Chapter 12 record bindings changed.",
            expected=expected_record_bindings,
            observed=declared.get("each_record_must_bind"),
        )

    source_map_path = _safe_relative_path(
        root, str(declared.get("generated_source_map", "")), label="generated source map"
    )
    audit_path = _safe_relative_path(
        root, str(declared.get("generated_audit", "")), label="generated reporting audit"
    )
    source_map_present = source_map_path.is_file()
    audit_present = audit_path.is_file()
    result["generated_source_map_present"] = source_map_present
    result["generated_audit_present"] = audit_present

    # A source map without the final reporting audit is a normal intermediate
    # state after the Python route and before R parity.  Static bindings remain
    # authoritative until both final generated reporting artifacts are present.
    if not audit_present:
        result["generated_output_check"] = (
            "DEFERRED_INTERMEDIATE_SOURCE_MAP"
            if source_map_present
            else "NOT_PRESENT"
        )
        result["status"] = (
            FAIL if collector.has_category(REPORTING_CATEGORY) else PASS
        )
        return result

    if audit_present and not source_map_present:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The final reporting audit exists without its source map.",
            generated_audit=declared.get("generated_audit"),
            generated_source_map=declared.get("generated_source_map"),
        )
        result["generated_output_check"] = "FAIL"
        result["status"] = FAIL
        return result

    try:
        source_map = _load_json_object(source_map_path, label="generated Chapter 12 source map")
        reporting_audit = _load_json_object(audit_path, label="generated Chapter 12 audit")
    except ContractError as exc:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            str(exc),
        )
        result["generated_output_check"] = "FAIL"
        result["status"] = FAIL
        return result

    if source_map.get("schema_version") != "book1-apa-source-map-v0.1":
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated Chapter 12 source-map schema is unexpected.",
            observed_schema=source_map.get("schema_version"),
        )
    if source_map.get("synthetic_data_only") is not True:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated Chapter 12 source map does not remain synthetic-only.",
        )

    records = source_map.get("records")
    if not isinstance(records, list):
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated Chapter 12 source map lacks a record list.",
        )
        records = []

    records_by_chapter: dict[str, Mapping[str, Any]] = {}
    duplicates: list[str] = []
    for row in records:
        if not isinstance(row, dict) or not isinstance(row.get("chapter"), str):
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                scope,
                "A generated source-map record lacks a chapter identifier.",
            )
            continue
        chapter_id = str(row["chapter"])
        if chapter_id in records_by_chapter:
            duplicates.append(chapter_id)
        records_by_chapter[chapter_id] = row
    if duplicates:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated source map contains duplicate chapter records.",
            duplicate_chapters=sorted(set(duplicates)),
        )

    result_records: list[dict[str, Any]] = []
    for chapter_id in expected_chapters:
        chapter = contract["chapters"][chapter_id]
        binding = chapter["analysis_binding"]
        record = records_by_chapter.get(chapter_id)
        record_result: dict[str, Any] = {
            "chapter": chapter_id,
            "present": record is not None,
        }
        if record is None:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "The generated source map is missing a required chapter record.",
            )
            result_records.append(record_result)
            continue

        expected_paths = {
            "python_result_file": binding["outputs"]["python_result"],
            "r_result_file": binding["outputs"]["r_result"],
            "parity_receipt": binding["outputs"]["parity_receipt"],
        }
        actual_paths = {
            name: record.get(name) for name in expected_paths
        }
        record_result["expected_paths"] = expected_paths
        record_result["actual_paths"] = actual_paths
        if actual_paths != expected_paths:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "A generated source-map record points to the wrong result or parity path.",
                expected=expected_paths,
                actual=actual_paths,
            )
        if record.get("analysis_name") != binding.get("method"):
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "A generated source-map analysis name does not match the contract.",
                expected=binding.get("method"),
                actual=record.get("analysis_name"),
            )

        bound_paths: dict[str, Path] = {}
        for name, rel in expected_paths.items():
            bound_paths[name] = _safe_relative_path(
                root, rel, label=f"{chapter_id} reporting {name}"
            )
        py_path = bound_paths["python_result_file"]
        r_path = bound_paths["r_result_file"]
        parity_path = bound_paths["parity_receipt"]
        if not py_path.is_file() or not r_path.is_file() or not parity_path.is_file():
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "A final generated source-map record points to a missing result or parity artifact.",
                python_result_present=py_path.is_file(),
                r_result_present=r_path.is_file(),
                parity_receipt_present=parity_path.is_file(),
            )
            result_records.append(record_result)
            continue

        try:
            py_payload = _load_json_object(py_path, label=f"{chapter_id} Python result")
            r_payload = _load_json_object(r_path, label=f"{chapter_id} R result")
        except ContractError as exc:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                str(exc),
            )
            result_records.append(record_result)
            continue

        py_hash = sha256_file(py_path)
        if record.get("source_sha256") != py_hash:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "A generated source-map Python-result fingerprint is stale or incorrect.",
                expected=py_hash,
                actual=record.get("source_sha256"),
            )
        if py_payload.get("data_file") != chapter.get("source_csv"):
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "The Python result records a different source CSV than the design contract.",
                expected=chapter.get("source_csv"),
                actual=py_payload.get("data_file"),
            )
        if r_payload.get("data_file") != chapter.get("source_csv"):
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "The R result records a different source CSV than the design contract.",
                expected=chapter.get("source_csv"),
                actual=r_payload.get("data_file"),
            )
        if py_payload.get("analysis_name") != binding.get("method") or r_payload.get(
            "analysis_name"
        ) != binding.get("method"):
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "A generated result analysis name does not match the design contract.",
                expected=binding.get("method"),
                python_actual=py_payload.get("analysis_name"),
                r_actual=r_payload.get("analysis_name"),
            )
        fields = py_payload.get("reported_fields")
        apa_result_matches = False
        if not isinstance(fields, dict) or record.get("reported_fields") != fields:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "The source-map reported fields do not match the Python result.",
            )
        else:
            try:
                expected_sentence = _expected_apa_sentence(chapter_id, fields)
            except (KeyError, TypeError, ValueError) as exc:
                collector.add(
                    REPORTING_CATEGORY,
                    "REPORTING_BINDING_MISMATCH",
                    f"{scope}.{chapter_id}",
                    "The approved APA sentence could not be reconstructed from the Python fields.",
                    error=str(exc),
                )
            else:
                apa_result_matches = record.get("apa_result") == expected_sentence
                if not apa_result_matches:
                    collector.add(
                        REPORTING_CATEGORY,
                        "REPORTING_BINDING_MISMATCH",
                        f"{scope}.{chapter_id}",
                        "The generated APA sentence does not match the approved source-bound formatter.",
                        expected=expected_sentence,
                        actual=record.get("apa_result"),
                    )
        try:
            parity_text = parity_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            parity_text = ""
        if "Status: PASS" not in parity_text:
            collector.add(
                REPORTING_CATEGORY,
                "REPORTING_BINDING_MISMATCH",
                f"{scope}.{chapter_id}",
                "The final reporting route does not have a passed parity receipt.",
                parity_receipt=expected_paths["parity_receipt"],
            )

        record_result.update(
            {
                "python_result_sha256": py_hash,
                "python_result_source_hash_matches": record.get("source_sha256") == py_hash,
                "parity_receipt_pass": "Status: PASS" in parity_text,
                "apa_result_matches": apa_result_matches,
            }
        )
        result_records.append(record_result)

    unexpected_chapters = sorted(set(records_by_chapter) - set(expected_chapters))
    if unexpected_chapters:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated source map contains unexpected chapter records.",
            unexpected_chapters=unexpected_chapters,
        )

    if reporting_audit.get("schema_version") != "book1-apa-reporting-audit-v0.1":
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated Chapter 12 reporting-audit schema is unexpected.",
            observed_schema=reporting_audit.get("schema_version"),
        )
    if reporting_audit.get("synthetic_data_only") is not True:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated reporting audit does not remain synthetic-only.",
        )
    if reporting_audit.get("source_record_count") != len(expected_chapters):
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated reporting-audit record count does not match the contract.",
            expected=len(expected_chapters),
            actual=reporting_audit.get("source_record_count"),
        )
    if reporting_audit.get("all_apa_examples_sourced") is not True:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated reporting audit does not confirm all APA examples are sourced.",
        )
    if reporting_audit.get("all_parity_receipts_pass") is not True:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated reporting audit does not confirm all parity receipts pass.",
        )
    if reporting_audit.get("failures") != []:
        collector.add(
            REPORTING_CATEGORY,
            "REPORTING_BINDING_MISMATCH",
            scope,
            "The generated reporting audit contains failures.",
            failures=reporting_audit.get("failures"),
        )

    result["records"] = result_records
    result["generated_output_check"] = (
        FAIL if collector.has_category(REPORTING_CATEGORY) else PASS
    )
    result["status"] = (
        FAIL if collector.has_category(REPORTING_CATEGORY) else PASS
    )
    return result


# ---------------------------------------------------------------------------
# Public audit and deterministic outputs
# ---------------------------------------------------------------------------


def audit_companion(
    root: Path | str = ROOT,
    *,
    contract_path: Path | str | None = None,
    source_overrides: Mapping[str, Path | str] | None = None,
) -> dict[str, Any]:
    """Audit a companion root and return a deterministic receipt object.

    ``source_overrides`` is primarily for tests and controlled historical
    negative controls.  Keys are chapter IDs and values are alternate CSV paths.
    The override changes only that chapter's source bytes; all contract bindings
    remain anchored to the declared companion root.
    """

    root_path = Path(root).resolve()
    contract, resolved_contract_path, contract_hash = load_contract(
        root_path, contract_path
    )
    collector = FailureCollector(contract["failure_codes"])
    overrides = {
        str(key): Path(value).resolve()
        for key, value in (source_overrides or {}).items()
    }

    chapter_receipts: dict[str, Any] = {}
    for chapter_id, chapter in contract["chapters"].items():
        scope = f"chapters.{chapter_id}"
        source_rel = str(chapter["source_csv"])
        source_path = overrides.get(
            chapter_id,
            _safe_relative_path(root_path, source_rel, label=f"{chapter_id} source CSV"),
        )
        profile = _read_csv_profile(
            source_path,
            source_rel,
            chapter,
            collector,
            scope,
        )
        records = profile.records()
        design_type = str(chapter.get("design_type", ""))
        if design_type.startswith("independent_groups_"):
            semantic_summary = _check_independent_design(
                chapter_id,
                chapter,
                records,
                collector,
                scope,
            )
        elif design_type == "paired_wide_one_row_per_participant":
            semantic_summary = _check_paired_design(
                chapter,
                records,
                collector,
                scope,
            )
        elif design_type == "repeated_measures_long_complete_three_occasion":
            semantic_summary = _check_repeated_design(
                chapter,
                records,
                collector,
                scope,
            )
        elif design_type in {
            "one_observational_pair_per_participant",
            "one_predictor_outcome_pair_per_participant",
        }:
            semantic_summary = _check_observational_pair_design(
                chapter,
                records,
                profile.numeric_profiles,
                collector,
                scope,
            )
        else:
            collector.add(
                SEMANTIC_CATEGORY,
                "MISSING_REQUIRED_VALUE",
                scope,
                "The chapter declares an unsupported design type.",
                design_type=design_type,
            )
            semantic_summary = {}

        fingerprint_checks = _check_release_fingerprint(
            chapter_id,
            chapter,
            profile,
            records,
            semantic_summary,
            collector,
            scope,
        )
        analysis_observations = _check_analysis_binding(
            root_path,
            chapter_id,
            chapter,
            collector,
            scope,
        )
        figure_contract = chapter.get("figure_binding", {})
        chapter_receipts[chapter_id] = {
            "title": chapter.get("title"),
            "research_question": chapter.get("research_question"),
            "design_type": design_type,
            "source_csv": source_rel,
            "source_override_used": chapter_id in overrides,
            "source_sha256": profile.source_sha256,
            "source_byte_count": profile.byte_count,
            "row_count": profile.row_count,
            "columns": profile.header,
            "row_width_mismatch_count": profile.row_width_mismatch_count,
            "missing_value_counts": profile.missing_value_counts,
            "leading_or_trailing_whitespace_counts": profile.whitespace_counts,
            "exact_duplicate_row_count": profile.exact_duplicate_row_count,
            "numeric_profiles": profile.numeric_profiles,
            "design_observations": semantic_summary,
            "release_fingerprint_checks": fingerprint_checks,
            "analysis_binding": analysis_observations,
            "figure_binding": figure_contract,
        }

    # Cross-companion separation is a semantic rule, not a requirement that
    # identifiers be globally unique across chapter datasets.
    cross = contract["cross_companion_rules"]
    ch10_path = overrides.get(
        "ch10",
        _safe_relative_path(
            root_path,
            contract["chapters"]["ch10"]["source_csv"],
            label="Chapter 10 source CSV",
        ),
    )
    ch11_path = overrides.get(
        "ch11",
        _safe_relative_path(
            root_path,
            contract["chapters"]["ch11"]["source_csv"],
            label="Chapter 11 source CSV",
        ),
    )
    ch10_hash = sha256_file(ch10_path) if ch10_path.is_file() else None
    ch11_hash = sha256_file(ch11_path) if ch11_path.is_file() else None
    hashes_distinct = ch10_hash is not None and ch11_hash is not None and ch10_hash != ch11_hash
    bytes_distinct = (
        ch10_path.is_file()
        and ch11_path.is_file()
        and ch10_path.read_bytes() != ch11_path.read_bytes()
    )
    if cross.get("ch10_and_ch11_source_files_must_be_distinct") is True and not (
        hashes_distinct and bytes_distinct
    ):
        collector.add(
            SEMANTIC_CATEGORY,
            "CROSS_FILE_SOURCE_COLLISION",
            "cross_companion_rules",
            "Chapter 10 and Chapter 11 must remain distinct teaching sources.",
            ch10_sha256=ch10_hash,
            ch11_sha256=ch11_hash,
        )
    cross_receipt = {
        "chapter_ids_are_not_cross_dataset_subject_links": bool(
            cross.get("chapter_ids_are_not_cross_dataset_subject_links")
        ),
        "ch10_source_sha256": ch10_hash,
        "ch11_source_sha256": ch11_hash,
        "ch10_ch11_hashes_distinct": hashes_distinct,
        "ch10_ch11_bytes_distinct": bytes_distinct,
    }

    figure_receipt = _check_figure_bindings(root_path, contract, collector)
    reporting_receipt = _check_reporting_bindings(root_path, contract, collector)

    # Apply global figure/reporting outcomes to chapter-level status fields.
    required_figure_ids = {
        row.get("figure_id")
        for row in contract["figure_bindings"].get("figures", [])
        if isinstance(row, dict)
    }
    for chapter_id, chapter_receipt in chapter_receipts.items():
        scope = f"chapters.{chapter_id}"
        chapter_receipt["semantic_design_status"] = (
            FAIL if collector.has_category(SEMANTIC_CATEGORY, scope=scope) else PASS
        )
        chapter_receipt["release_fingerprint_status"] = (
            FAIL if collector.has_category(RELEASE_CATEGORY, scope=scope) else PASS
        )
        chapter_receipt["analysis_binding_status"] = (
            FAIL if collector.has_category(ANALYSIS_CATEGORY, scope=scope) else PASS
        )
        figure_binding = contract["chapters"][chapter_id].get("figure_binding", {})
        if figure_binding.get("status") == "NOT_APPLICABLE":
            chapter_receipt["figure_binding_status"] = NOT_APPLICABLE
        else:
            figure_id = figure_binding.get("figure_id")
            figure_failed = collector.has_category(FIGURE_CATEGORY, scope=scope) or collector.has_category(
                FIGURE_CATEGORY, scope=f"figure_bindings.{figure_id}"
            )
            if figure_id not in required_figure_ids:
                figure_failed = True
            chapter_receipt["figure_binding_status"] = FAIL if figure_failed else PASS
        chapter_receipt["reporting_binding_status"] = (
            FAIL
            if collector.has_category(
                REPORTING_CATEGORY, scope=f"reporting_bindings.{chapter_id}"
            )
            else PASS
        )
        chapter_receipt["failure_codes"] = sorted(
            {row.code for row in collector.for_scope(scope)}
        )
        chapter_receipt["failures"] = [
            row.as_dict() for row in collector.for_scope(scope)
        ]

    failures = collector.rows()
    top_statuses = {
        status_key: FAIL
        if collector.has_category(category)
        else PASS
        for category, status_key in CATEGORY_TO_STATUS.items()
    }
    overall_status = PASS if all(value == PASS for value in top_statuses.values()) else FAIL

    try:
        contract_rel = resolved_contract_path.relative_to(root_path).as_posix()
    except ValueError:
        contract_rel = resolved_contract_path.as_posix()

    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "companion_version": contract["companion_version"],
        "required_pystatsv1_release": contract["required_pystatsv1_release"],
        "synthetic_data_only": True,
        "contract": {
            "path": contract_rel,
            "sha256": contract_hash,
            "schema_version": contract["schema_version"],
        },
        **top_statuses,
        "overall_status": overall_status,
        "failure_codes": sorted({row.code for row in failures}),
        "failures": [row.as_dict() for row in failures],
        "chapters": chapter_receipts,
        "cross_companion_rules": cross_receipt,
        "figure_bindings": figure_receipt,
        "reporting_bindings": reporting_receipt,
        "limits": list(contract["framework"].get("limits", [])),
    }
    return _json_safe(receipt)


def render_markdown_summary(receipt: Mapping[str, Any]) -> str:
    """Render a compact, deterministic Markdown companion to the JSON receipt."""

    lines = [
        "# Book 1 Design Audit Summary",
        "",
        f"Overall status: **{receipt['overall_status']}**",
        "",
        "## Layer statuses",
        "",
    ]
    labels = {
        "semantic_design_status": "Semantic design and data layout",
        "release_fingerprint_status": "Exact release fingerprint",
        "analysis_binding_status": "Analysis binding",
        "figure_binding_status": "Figure binding",
        "reporting_binding_status": "Reporting binding",
    }
    for key in STATUS_KEYS:
        lines.append(f"- {labels[key]}: **{receipt[key]}**")

    lines.extend(["", "## Chapter statuses", ""])
    lines.append(
        "| Chapter | Semantic design | Release fingerprint | Analysis | Figure | Reporting |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    for chapter_id, chapter in receipt["chapters"].items():
        lines.append(
            f"| {chapter_id} | {chapter['semantic_design_status']} | "
            f"{chapter['release_fingerprint_status']} | "
            f"{chapter['analysis_binding_status']} | "
            f"{chapter['figure_binding_status']} | "
            f"{chapter['reporting_binding_status']} |"
        )

    failures = receipt.get("failures", [])
    lines.extend(["", "## Failures", ""])
    if failures:
        for row in failures:
            lines.append(
                f"- `{row['code']}` — `{row['scope']}` — {row['message']}"
            )
    else:
        lines.append("No design-contract failures were detected.")

    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "This audit checks the documented synthetic teaching design, exact release "
            "fingerprints, and declared analysis/figure/reporting bindings. It does not "
            "establish measurement validity, ethical authorization, assumption adequacy, "
            "causal identification, practical importance, or generalizability.",
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.chmod(0o644)
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def write_audit_outputs(
    receipt: Mapping[str, Any],
    root: Path | str = ROOT,
    *,
    json_path: Path | str | None = None,
    markdown_path: Path | str | None = None,
) -> tuple[Path, Path]:
    """Atomically write deterministic JSON and Markdown audit outputs."""

    root_path = Path(root).resolve()
    contract, _, _ = load_contract(root_path)
    receipt_contract = contract["receipt_contract"]
    json_out = (
        Path(json_path).resolve()
        if json_path is not None
        else _safe_relative_path(
            root_path,
            receipt_contract["generated_json"],
            label="design-audit JSON output",
        )
    )
    markdown_out = (
        Path(markdown_path).resolve()
        if markdown_path is not None
        else _safe_relative_path(
            root_path,
            receipt_contract["generated_markdown"],
            label="design-audit Markdown output",
        )
    )
    _atomic_write(json_out, canonical_json_bytes(receipt))
    _atomic_write(markdown_out, render_markdown_summary(receipt).encode("utf-8"))
    return json_out, markdown_out


def receipt_status_line(receipt: Mapping[str, Any]) -> str:
    """Return a deterministic one-line status suitable for terminal logs."""

    codes = ",".join(receipt.get("failure_codes", [])) or "none"
    return (
        f"overall={receipt['overall_status']} "
        f"semantic={receipt['semantic_design_status']} "
        f"fingerprint={receipt['release_fingerprint_status']} "
        f"analysis={receipt['analysis_binding_status']} "
        f"figure={receipt['figure_binding_status']} "
        f"reporting={receipt['reporting_binding_status']} "
        f"failure_codes={codes}"
    )


__all__ = [
    "ContractError",
    "PASS",
    "FAIL",
    "NOT_APPLICABLE",
    "ROOT",
    "STATUS_KEYS",
    "audit_companion",
    "canonical_json_bytes",
    "load_contract",
    "receipt_status_line",
    "render_markdown_summary",
    "sha256_file",
    "write_audit_outputs",
]
