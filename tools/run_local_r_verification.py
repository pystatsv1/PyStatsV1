#!/usr/bin/env python3
"""Run all governed R parity checks locally and write a runtime receipt.

GitHub-hosted workflows intentionally do not install or execute R. This command is the
single local gate for the three Psychological Statistics by Design batches and the
current public Book 1 companion. It assumes the caller has prepared the governed
Python environment documented in ``docs/LOCAL_R_VERIFICATION_POLICY.md``.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "build" / "local_r_verification" / "LOCAL_R_VERIFICATION_RECEIPT.json"
MARKER = "PYSTATSV1_LOCAL_R_VERIFICATION_OK"


def run(command: list[str], *, cwd: Path = ROOT) -> dict[str, Any]:
    print("+", " ".join(command), flush=True)
    started = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, check=False)
    elapsed = round(time.monotonic() - started, 3)
    if completed.returncode != 0:
        raise RuntimeError(
            f"local R verification command failed with exit code {completed.returncode}: "
            + " ".join(command)
        )
    return {
        "command": command,
        "cwd": str(cwd.relative_to(ROOT) if cwd != ROOT else Path(".")),
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
    }


def capture(command: list[str], *, cwd: Path = ROOT) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def require_r() -> dict[str, str]:
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError(
            "Rscript is required for local R verification. "
            "On Ubuntu install r-base and r-cran-nlme before continuing."
        )
    version = capture([rscript, "--version"]).splitlines()[0]
    nlme = capture(
        [
            rscript,
            "-e",
            "if (!requireNamespace('nlme', quietly=TRUE)) quit(status=2); "
            "cat(as.character(packageVersion('nlme')))",
        ]
    )
    return {"rscript": rscript, "r_version": version, "nlme_version": nlme}


def git_value(*args: str) -> str:
    return capture(["git", *args])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable from the governed local verification environment",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=DEFAULT_RECEIPT,
        help="Runtime receipt path (normally under ignored build/)",
    )
    parser.add_argument(
        "--skip-book1",
        action="store_true",
        help="Skip the current public Book 1 companion parity gate",
    )
    return parser.parse_args()


def normalize_python_executable(raw: str) -> str:
    """Return an absolute executable path without resolving virtualenv symlinks."""
    expanded = Path(raw).expanduser()
    python = Path(os.path.abspath(os.fspath(expanded)))
    if not python.is_file():
        raise RuntimeError(f"Python executable does not exist: {python}")
    return str(python)


def main() -> int:
    args = parse_args()
    python = normalize_python_executable(args.python)

    r_info = require_r()
    commands: list[dict[str, Any]] = []

    make = ["make", f"PYTHON={python}"]
    targets = [
        "psych-design-swl-s02-s05-verify",
        "psych-design-swl-s02-s05-r-verify",
        "psych-design-swl-s01-s06-s07-environment-verify",
        "psych-design-swl-s01-s06-s07-verify",
        "psych-design-swl-s01-s06-s07-r-verify",
        "psych-design-swl-s08-s10-verify",
        "psych-design-swl-s08-s10-r-verify",
    ]
    for target in targets:
        commands.append(run([*make, target]))

    if not args.skip_book1:
        companion = ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2_1"
        for target in ("design-audit", "python-only", "r-check", "parity"):
            commands.append(
                run(
                    ["make", f"PYTHON={python}", target],
                    cwd=companion,
                )
            )

    receipt_path = args.receipt.expanduser()
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    status = git_value("status", "--porcelain=v1", "--untracked-files=all")
    payload = {
        "schema_version": "pystatsv1-local-r-verification-receipt-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": "pystatsv1/PyStatsV1",
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_branch": git_value("branch", "--show-current"),
        "python_executable": python,
        "python_version": capture([python, "--version"]),
        "r": r_info,
        "book1_companion_included": not args.skip_book1,
        "commands": commands,
        "git_worktree_clean_after_verification": status == "",
        "success_marker": MARKER,
    }
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if status:
        raise RuntimeError(
            "local R verification changed tracked or untracked source paths:\n" + status
        )

    print(f"LOCAL_R_VERIFICATION_RECEIPT={receipt_path}")
    print(MARKER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
