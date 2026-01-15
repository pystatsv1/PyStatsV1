from __future__ import annotations

import argparse
import os
import platform
import sys
import textwrap
import zipfile
from importlib import metadata, resources
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
            f"""\
            ✅ Workbook starter created at:

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


def _dist_version(dist_name: str) -> str:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "not installed"
    except Exception:
        return "unknown"


_REQUIRED_IMPORTS: Final[list[tuple[str, str]]] = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("scipy", "scipy"),
    ("statsmodels", "statsmodels"),
    ("matplotlib", "matplotlib"),
    ("pingouin", "pingouin"),
    ("sklearn", "scikit-learn"),
]


def cmd_doctor(args: argparse.Namespace) -> int:
    ok = True

    in_venv = _in_venv()
    if not in_venv:
        print(
            "⚠️  You are NOT in a virtual environment. This is OK, but not recommended.\n"
            "Create one and activate it first:\n"
            "  python -m venv .venv\n"
            "  source .venv/Scripts/activate   # Windows Git Bash\n"
            "  source .venv/bin/activate       # macOS/Linux\n"
        )

    if getattr(args, "verbose", False):
        print("Environment")
        print(f"  python: {sys.version.splitlines()[0]}")
        print(f"  executable: {sys.executable}")
        print(f"  platform: {platform.platform()}")
        print(f"  venv: {'yes' if in_venv else 'no'}")
        print("\nPackages")

    missing: list[str] = []

    # Lightweight import checks (avoid crashing if optional deps are missing)
    for mod, dist in _REQUIRED_IMPORTS:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)

        if getattr(args, "verbose", False):
            print(f"  - {mod}: {_dist_version(dist)}")

    if missing:
        ok = False
        print(
            "\n❌ Missing packages in this environment:\n  - "
            + "\n  - ".join(missing)
            + "\n\nInstall the student bundle:\n"
            "  python -m pip install -U pip\n"
            "  python -m pip install \"pystatsv1[workbook]\"\n"
        )

    if ok:
        if in_venv:
            print("✅ Environment looks good.")
        else:
            print("✅ Packages look good (consider using a venv).")
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
    p_doctor.add_argument(
        "--verbose",
        action="store_true",
        help="Print Python/platform info and package versions.",
    )
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
