#!/usr/bin/env python3
"""Run the Book 1 companion design-contract audit.

By default the command writes deterministic JSON and Markdown evidence under
``outputs/design/``.  ``--check-only`` performs the same audit without writing
those generated files; the asset builder uses that mode so packaging never
modifies the source snapshot.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from book1_design_contract import (
    ContractError,
    PASS,
    ROOT,
    audit_companion,
    receipt_status_line,
    write_audit_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Companion root containing BOOK1_DESIGN_CONTRACT.json.",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=None,
        help="Optional explicit contract path. Defaults to ROOT/BOOK1_DESIGN_CONTRACT.json.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run the full audit without writing generated receipt files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        receipt = audit_companion(
            root,
            contract_path=args.contract,
        )
        if not args.check_only:
            json_out, markdown_out = write_audit_outputs(receipt, root)
            print(f"wrote {json_out}")
            print(f"wrote {markdown_out}")
    except ContractError as exc:
        print(f"BOOK1_COMPANION_DESIGN_AUDIT_CONTRACT_ERROR: {exc}", file=sys.stderr)
        return 2

    print(receipt_status_line(receipt))
    if receipt["overall_status"] != PASS:
        print("BOOK1_COMPANION_DESIGN_AUDIT_FAILED", file=sys.stderr)
        for failure in receipt["failures"]:
            print(
                f"{failure['code']} [{failure['scope']}]: {failure['message']}",
                file=sys.stderr,
            )
        return 1

    print("BOOK1_COMPANION_DESIGN_AUDIT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
