#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from common import OUTPUTS, sha256


def main() -> None:
    source_map_path = OUTPUTS / "ch12" / "apa_reporting_source_map.json"
    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    records = source_map["records"]
    failures = []
    for record in records:
        result_path = OUTPUTS / record["chapter"] / "py_results.json"
        receipt_path = OUTPUTS / record["chapter"] / "parity_receipt.md"
        if sha256(result_path) != record["source_sha256"]:
            failures.append(f"source hash drift: {record['chapter']}")
        if not receipt_path.exists() or "Status: PASS" not in receipt_path.read_text(encoding="utf-8"):
            failures.append(f"parity receipt not passed: {record['chapter']}")
    audit = {
        "schema_version": "book1-apa-reporting-audit-v0.1",
        "synthetic_data_only": True,
        "source_record_count": len(records),
        "all_apa_examples_sourced": not failures,
        "all_parity_receipts_pass": not failures,
        "failures": failures,
    }
    out = OUTPUTS / "ch12" / "apa_reporting_audit.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("; ".join(failures))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
