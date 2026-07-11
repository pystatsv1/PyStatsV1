#!/usr/bin/env python3
"""Permanent mutation tests for the Book 1 design contract.

The tests use temporary companion copies only.  They never alter the canonical
synthetic CSVs, historical assets, or approved release fingerprints.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_SCRIPTS = ROOT / "scripts" / "python"
if str(PYTHON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PYTHON_SCRIPTS))

from book1_design_contract import (  # noqa: E402
    FAIL,
    PASS,
    audit_companion,
    canonical_json_bytes,
    render_markdown_summary,
)


class Book1DesignContractTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self._temporary_directories: list[tempfile.TemporaryDirectory[str]] = []

    def tearDown(self) -> None:
        for directory in reversed(self._temporary_directories):
            directory.cleanup()

    def copy_companion(self, *, include_outputs: bool = False) -> Path:
        holder = tempfile.TemporaryDirectory(prefix="book1-design-contract-test-")
        self._temporary_directories.append(holder)
        destination = Path(holder.name) / "companion"

        def ignore(_directory: str, names: list[str]) -> set[str]:
            ignored = {
                name
                for name in names
                if name in {"__pycache__", ".pytest_cache"}
                or name.endswith((".pyc", ".pyo"))
            }
            if not include_outputs and "outputs" in names:
                ignored.add("outputs")
            return ignored

        shutil.copytree(ROOT, destination, ignore=ignore)
        return destination

    @staticmethod
    def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return rows[0], rows[1:]

    @staticmethod
    def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)

    @staticmethod
    def codes(receipt: dict) -> set[str]:
        return set(receipt["failure_codes"])

    def assert_code(self, receipt: dict, code: str) -> None:
        self.assertIn(code, self.codes(receipt), json.dumps(receipt["failures"], indent=2))

    def test_clean_contract_passes(self) -> None:
        receipt = audit_companion(ROOT)
        self.assertEqual(receipt["overall_status"], PASS)
        self.assertEqual(receipt["failure_codes"], [])
        for key in (
            "semantic_design_status",
            "release_fingerprint_status",
            "analysis_binding_status",
            "figure_binding_status",
            "reporting_binding_status",
        ):
            self.assertEqual(receipt[key], PASS)

    def test_clean_contract_passes_without_generated_outputs(self) -> None:
        root = self.copy_companion(include_outputs=False)
        receipt = audit_companion(root)
        self.assertEqual(receipt["overall_status"], PASS)
        self.assertEqual(
            receipt["reporting_bindings"]["generated_output_check"],
            "NOT_PRESENT",
        )

    def test_ch09_repeated_participant_ids_are_valid_by_design(self) -> None:
        receipt = audit_companion(ROOT)
        ch09 = receipt["chapters"]["ch09"]
        self.assertEqual(ch09["semantic_design_status"], PASS)
        self.assertEqual(
            ch09["design_observations"]["frequency_distribution"],
            {"3": 18},
        )
        self.assertEqual(
            ch09["design_observations"]["duplicate_subject_occasion_keys"],
            [],
        )

    def test_missing_required_column_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        index = header.index("group")
        self.write_csv(path, [name for name in header if name != "group"], [row[:index] + row[index + 1 :] for row in rows])
        receipt = audit_companion(root)
        self.assert_code(receipt, "MISSING_REQUIRED_COLUMN")
        self.assertEqual(receipt["chapters"]["ch05"]["semantic_design_status"], FAIL)

    def test_unexpected_column_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        self.write_csv(path, header + ["unexpected"], [row + ["x"] for row in rows])
        receipt = audit_companion(root)
        self.assert_code(receipt, "UNEXPECTED_COLUMN")

    def test_column_order_mismatch_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch06_paired.csv"
        header, rows = self.read_csv(path)
        order = [0, 2, 1]
        self.write_csv(path, [header[i] for i in order], [[row[i] for i in order] for row in rows])
        receipt = audit_companion(root)
        self.assert_code(receipt, "COLUMN_ORDER_MISMATCH")

    def test_blank_identifier_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        rows[0][header.index("participant_id")] = ""
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "MISSING_REQUIRED_VALUE")
        self.assert_code(receipt, "EMPTY_IDENTIFIER")

    def test_leading_or_trailing_whitespace_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        rows[0][header.index("group")] = " structured"
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "LEADING_OR_TRAILING_WHITESPACE")

    def test_unexpected_factor_level_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch07_one_way_anova.csv"
        header, rows = self.read_csv(path)
        rows[0][header.index("study_condition")] = "mystery_condition"
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "UNEXPECTED_FACTOR_LEVEL")

    def test_missing_factor_cell_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch08_two_way_anova.csv"
        header, rows = self.read_csv(path)
        strategy = header.index("strategy")
        feedback = header.index("feedback")
        rows = [
            row
            for row in rows
            if not (row[strategy] == "standard" and row[feedback] == "feedback")
        ]
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "MISSING_FACTOR_CELL")

    def test_nonnumeric_required_value_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        rows[0][header.index("test_score")] = "not-a-number"
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "NONNUMERIC_REQUIRED_VALUE")

    def test_nan_and_infinities_are_detected(self) -> None:
        for token in ("NaN", "inf", "-inf"):
            with self.subTest(token=token):
                root = self.copy_companion()
                path = root / "data" / "ch06_paired.csv"
                header, rows = self.read_csv(path)
                rows[0][header.index("anxiety_post")] = token
                self.write_csv(path, header, rows)
                receipt = audit_companion(root)
                self.assert_code(receipt, "NONFINITE_NUMERIC_VALUE")

    def test_exact_duplicate_row_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        rows.append(list(rows[0]))
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "EXACT_DUPLICATE_ROW")
        self.assert_code(receipt, "INDEPENDENT_DESIGN_ID_NOT_UNIQUE")

    def test_historical_ch08_id_reuse_fails_with_stable_code(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch08_two_way_anova.csv"
        header, rows = self.read_csv(path)
        id_index = header.index("participant_id")
        for index, row in enumerate(rows):
            row[id_index] = f"ch08_{(index % 24) + 1:03d}"
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "INDEPENDENT_DESIGN_ID_NOT_UNIQUE")
        self.assertEqual(receipt["chapters"]["ch08"]["semantic_design_status"], FAIL)

    def test_duplicate_subject_occasion_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch09_repeated_measures.csv"
        header, rows = self.read_csv(path)
        rows.append(list(rows[0]))
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "DUPLICATE_SUBJECT_OCCASION")

    def test_incomplete_repeated_trajectory_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch09_repeated_measures.csv"
        header, rows = self.read_csv(path)
        self.write_csv(path, header, rows[1:])
        receipt = audit_companion(root)
        self.assert_code(receipt, "INCOMPLETE_REPEATED_TRAJECTORY")
        self.assert_code(receipt, "PIVOT_SHAPE_MISMATCH")

    def test_constant_predictor_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch11_regression.csv"
        header, rows = self.read_csv(path)
        index = header.index("study_hours")
        for row in rows:
            row[index] = "7.5"
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        self.assert_code(receipt, "CONSTANT_PREDICTOR")
        self.assert_code(receipt, "INSUFFICIENT_DISTINCT_PREDICTOR_VALUES")

    def test_semantic_pass_and_release_fingerprint_fail_can_coexist(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        score = header.index("test_score")
        rows[0][score] = str(float(rows[0][score]) + 0.001)
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        ch05 = receipt["chapters"]["ch05"]
        self.assertEqual(ch05["semantic_design_status"], PASS)
        self.assertEqual(ch05["release_fingerprint_status"], FAIL)
        self.assert_code(receipt, "SOURCE_FINGERPRINT_MISMATCH")

    def test_one_column_sorting_triggers_pairing_fingerprint(self) -> None:
        root = self.copy_companion()
        path = root / "data" / "ch10_correlation.csv"
        header, rows = self.read_csv(path)
        index = header.index("study_hours")
        sorted_values = sorted(float(row[index]) for row in rows)
        for row, value in zip(rows, sorted_values):
            row[index] = str(value)
        self.write_csv(path, header, rows)
        receipt = audit_companion(root)
        ch10 = receipt["chapters"]["ch10"]
        self.assertEqual(ch10["semantic_design_status"], PASS)
        self.assertEqual(ch10["release_fingerprint_status"], FAIL)
        self.assert_code(receipt, "PAIRING_FINGERPRINT_MISMATCH")

    def test_analysis_script_drift_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "scripts" / "python" / "ch05_independent_t.py"
        path.write_text(path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        receipt = audit_companion(root)
        self.assert_code(receipt, "ANALYSIS_BINDING_MISMATCH")
        self.assertEqual(receipt["analysis_binding_status"], FAIL)

    def test_figure_specification_drift_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "figures_specs.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["figures"][0]["source_csv"] = "data/ch11_regression.csv"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt = audit_companion(root)
        self.assert_code(receipt, "FIGURE_BINDING_MISMATCH")
        self.assertEqual(receipt["figure_binding_status"], FAIL)

    def test_reporting_script_drift_is_detected(self) -> None:
        root = self.copy_companion()
        path = root / "scripts" / "python" / "ch12_apa_reporting.py"
        path.write_text(path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        receipt = audit_companion(root)
        self.assert_code(receipt, "REPORTING_BINDING_MISMATCH")
        self.assertEqual(receipt["reporting_binding_status"], FAIL)

    def test_ch10_ch11_source_collision_is_detected(self) -> None:
        root = self.copy_companion()
        shutil.copyfile(
            root / "data" / "ch10_correlation.csv",
            root / "data" / "ch11_regression.csv",
        )
        receipt = audit_companion(root)
        self.assert_code(receipt, "CROSS_FILE_SOURCE_COLLISION")

    def test_check_only_cli_writes_no_outputs(self) -> None:
        root = self.copy_companion(include_outputs=False)
        completed = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "python" / "audit_design_contract.py"),
                "--root",
                str(root),
                "--check-only",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("BOOK1_COMPANION_DESIGN_AUDIT_OK", completed.stdout)
        self.assertFalse((root / "outputs" / "design").exists())

    def test_cli_writes_deterministic_receipts(self) -> None:
        root = self.copy_companion(include_outputs=False)
        command = [
            sys.executable,
            str(root / "scripts" / "python" / "audit_design_contract.py"),
            "--root",
            str(root),
        ]
        first = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        json_path = root / "outputs" / "design" / "BOOK1_DESIGN_AUDIT_RECEIPT.json"
        md_path = root / "outputs" / "design" / "BOOK1_DESIGN_AUDIT_SUMMARY.md"
        first_json = json_path.read_bytes()
        first_md = md_path.read_bytes()
        second = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(first_json, json_path.read_bytes())
        self.assertEqual(first_md, md_path.read_bytes())
        self.assertNotIn(b"timestamp", first_json.lower())
        self.assertIn("BOOK1_COMPANION_DESIGN_AUDIT_OK", second.stdout)

    def test_failing_cli_writes_structured_failure_receipt(self) -> None:
        root = self.copy_companion(include_outputs=False)
        path = root / "data" / "ch05_independent.csv"
        header, rows = self.read_csv(path)
        rows[0][header.index("participant_id")] = ""
        self.write_csv(path, header, rows)
        completed = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "python" / "audit_design_contract.py"),
                "--root",
                str(root),
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("BOOK1_COMPANION_DESIGN_AUDIT_FAILED", completed.stderr)
        self.assertNotIn("BOOK1_COMPANION_DESIGN_AUDIT_OK", completed.stdout)
        receipt = json.loads(
            (
                root
                / "outputs"
                / "design"
                / "BOOK1_DESIGN_AUDIT_RECEIPT.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["overall_status"], FAIL)
        self.assertIn("EMPTY_IDENTIFIER", receipt["failure_codes"])

    def test_public_renderers_are_deterministic(self) -> None:
        receipt = audit_companion(ROOT)
        self.assertEqual(canonical_json_bytes(receipt), canonical_json_bytes(receipt))
        self.assertEqual(render_markdown_summary(receipt), render_markdown_summary(receipt))


if __name__ == "__main__":
    unittest.main(verbosity=2)
