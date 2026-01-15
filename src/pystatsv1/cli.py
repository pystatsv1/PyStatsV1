from __future__ import annotations

import argparse
import os
import sys
import textwrap
import zipfile
from importlib import resources
from pathlib import Path
from typing import Final


PKG: Final[str] = "pystatsv1"


def _in_venv() -> bool:
    # Works for venv and virtualenv.
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def _open_file(path: Path) -> None:
    # Cross-platform "open in default app"
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        os.execvp("open", ["open", str(path)])
    else:
        os.execvp("xdg-open", ["xdg-open", str(path)])


def _get_packaged_pdf() -> Path | None:
    # Packaged as pystatsv1/docs/pystatsv1.pdf
    try:
        candidate = resources.files(PKG) / "docs" / "pystatsv1.pdf"
        with resources.as_file(candidate) as p:
            return Path(p)
    except Exception:
        return None


def cmd_docs(_: argparse.Namespace) -> int:
    pdf = _get_packaged_pdf()
    if pdf is None or not pdf.exists():
        print("Local docs PDF not found in this installation.")
        return 1

    print(f"Opening: {pdf}")
    _open_file(pdf)
    return 0


def _extract_workbook_template(dest: Path, force: bool) -> None:
    dest = dest.expanduser().resolve()

    if dest.exists():
        if any(dest.iterdir()) and not force:
            raise SystemExit(
                f"Refusing to write into non-empty directory: {dest}\n"
                "Use --force to overwrite into an existing directory."
            )
    else:
        dest.mkdir(parents=True, exist_ok=True)

    asset = resources.files(f"{PKG}.assets") / "workbook_starter.zip"
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            zf.extractall(dest)


def cmd_workbook_init(args: argparse.Namespace) -> int:
    _extract_workbook_template(Path(args.dest), force=args.force)

    dest = Path(args.dest).expanduser().resolve()
    print(
        textwrap.dedent(
            f"""            ✅ Workbook starter created at:

                {dest}

            Next steps:
              1) cd {dest}
              2) python scripts/psych_ch10_problem_set.py
              3) pytest -q

            Tip: If you're new to Python, always work inside a virtual environment.
            """
        ).rstrip()
    )
    return 0


def cmd_workbook_list(_: argparse.Namespace) -> int:
    # Just list what is bundled in the starter zip (Track C for now).
    chapters = [
        "Ch10  One-way ANOVA",
        "Ch11  Repeated measures / mixed designs (problem set)",
        "Ch12  Factorial designs",
        "Ch14  Nonparametric tests",
        "Ch15  Correlation & simple regression",
        "Ch16  Multiple regression",
        "Ch17  Logistic regression",
        "Ch18  ANCOVA",
        "Ch19  Mediation / moderation (intro)",
        "Ch20  Power / simulation (intro)",
    ]
    print("\n".join(chapters))
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    ok = True

    if not _in_venv():
        ok = False
        print(
            "⚠️  You are NOT in a virtual environment.\n"
            "Create one and activate it first (recommended):\n"
            "  python -m venv .venv\n"
            "  source .venv/Scripts/activate   # Windows Git Bash\n"
            "  source .venv/bin/activate       # macOS/Linux\n"
        )

    # Lightweight import checks (avoid crashing if optional deps are missing)
    required = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "pingouin", "sklearn"]
    missing: list[str] = []
    for mod in required:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)

    if missing:
        ok = False
        print(
            "❌ Missing packages in this environment:\n  - "
            + "\n  - ".join(missing)
            + "\n\nInstall the student bundle:\n"
            "  python -m pip install -U pip\n"
            "  python -m pip install \"pystatsv1[workbook]\"\n"
        )

    if ok:
        print("✅ Environment looks good.")
        return 0
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pystatsv1",
        description="PyStatsV1: treat statistical analysis like production software.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=_version_string(),
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_docs = sub.add_parser("docs", help="Open packaged PDF docs (if available).")
    p_docs.set_defaults(func=cmd_docs)

    p_doctor = sub.add_parser("doctor", help="Sanity-check your environment (venv + deps).")
    p_doctor.set_defaults(func=cmd_doctor)

    p_wb = sub.add_parser("workbook", help="Workbook helpers (student labs).")
    wb_sub = p_wb.add_subparsers(dest="workbook_cmd", required=True)

    p_init = wb_sub.add_parser("init", help="Create a local workbook starter folder.")
    p_init.add_argument(
        "--dest",
        default="pystatsv1_workbook",
        help="Destination directory to create (default: pystatsv1_workbook).",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing non-empty directory.",
    )
    p_init.set_defaults(func=cmd_workbook_init)

    p_list = wb_sub.add_parser("list", help="List chapters included in the starter kit.")
    p_list.set_defaults(func=cmd_workbook_list)

    return p


def _version_string() -> str:
    try:
        from importlib.metadata import version

        return version(PKG)
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


# Back-compat: allow a dedicated console script for docs if desired.
def docs_main(argv: list[str] | None = None) -> int:
    return main(["docs"] + ([] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
