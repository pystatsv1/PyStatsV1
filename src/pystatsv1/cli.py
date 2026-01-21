from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
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


def _normalize_track(track: str | None) -> str:
    t = (track or "c").strip().lower()
    if t in {"c", "track_c"}:
        return "c"
    if t in {"d", "track_d"}:
        return "d"
    raise SystemExit(
        "Unknown track. Use one of: c, track_c, d, track_d.\n"
        "Example: pystatsv1 workbook init --track d"
    )


def _workbook_asset_for_track(track: str) -> str:
    t = _normalize_track(track)
    return {
        "c": "workbook_starter.zip",
        "d": "workbook_track_d.zip",
    }[t]


def _extract_workbook_template(dest: Path, force: bool, track: str = "c") -> None:
    dest = dest.expanduser().resolve()

    if dest.exists():
        if any(dest.iterdir()) and not force:
            raise SystemExit(
                f"Refusing to write into non-empty directory: {dest}\n"
                "Use --force to overwrite into an existing directory."
            )
    else:
        dest.mkdir(parents=True, exist_ok=True)

    asset_name = _workbook_asset_for_track(track)
    asset = resources.files(f"{PKG}.assets") / asset_name
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            zf.extractall(dest)


def _extract_asset_zip(asset_name: str, dest: Path) -> None:
    asset = resources.files(f"{PKG}.assets") / asset_name
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            zf.extractall(dest)


def _extract_track_d_datasets(dest: Path) -> None:
    # Extract canonical Track D datasets (seed=123) into the workbook folder.
    ds_root = dest / "data" / "synthetic"
    ds_root.mkdir(parents=True, exist_ok=True)

    for asset_name in (
        "ledgerlab_ch01_seed123.zip",
        "nso_v1_seed123.zip",
    ):
        try:
            _extract_asset_zip(asset_name, ds_root)
        except Exception as e:
            raise SystemExit(
                "Failed to extract Track D canonical datasets. "
                "Try upgrading PyStatsV1 (pip install -U pystatsv1) and re-run workbook init. "
                f"Missing or unreadable asset: {asset_name}"
            ) from e


def cmd_workbook_init(args: argparse.Namespace) -> int:
    track = _normalize_track(getattr(args, "track", "c"))
    _extract_workbook_template(Path(args.dest), force=args.force, track=track)

    dest = Path(args.dest).expanduser().resolve()
    if track == "d":
        _extract_track_d_datasets(dest)
        next_steps = textwrap.dedent(
            f"""\
            OK: Track D workbook starter created at:

                {dest}

            Next steps:
              1) cd {dest}
              2) pystatsv1 workbook run d00_peek_data

            (Datasets are pre-installed under data/synthetic/, seed=123.)

            Tip: If you're new to Python, always work inside a virtual environment.
            """
        ).rstrip()
        print(next_steps)
        return 0

    print(
        textwrap.dedent(
            f"""\
            OK: Workbook starter created at:

                {dest}

            Next steps:
              1) cd {dest}
              2) pystatsv1 workbook run ch10
              3) pystatsv1 workbook check ch10

            Tip: If you're new to Python, always work inside a virtual environment.
            """
        ).rstrip()
    )
    return 0


def cmd_workbook_list(args: argparse.Namespace) -> int:
    track = _normalize_track(getattr(args, "track", "c"))

    if track == "d":
        chapters = [
            "D00  Setup/reset Track D datasets (run: d00_setup_data)",
            "D00  Peek the Track D datasets (LedgerLab + NSO) (run: d00_peek_data)",
            "D01  Ch01 Accounting as a measurement system (run: d01)",
            "D02  Ch02 Double-entry and the general ledger as a database (run: d02)",
            "D03  Ch03 Financial statements as summaries (run: d03)",
            "D04  Ch04 Assets: inventory + fixed assets (run: d04)",
            "D05  Ch05 Liabilities, payroll, taxes, and equity (run: d05)",
            "D06  Ch06 Reconciliations and quality control (run: d06)",
            "D07  Ch07 Preparing accounting data for analysis (run: d07)",
            "D08  Ch08 Descriptive statistics for financial performance (run: d08)",
            "D09  Ch09 Reporting style contract (run: d09)",
            "D10  Ch10 Probability and risk (run: d10)",
            "D11  Ch11 Sampling, estimation, and audit controls (run: d11)",
            "D12  Ch12 Hypothesis testing for decisions (run: d12)",
            "D13  Ch13 Correlation, causation, and controlled comparisons (run: d13)",
            "D14  Ch14 Regression and driver analysis (run: d14)",
            "D15  Ch15 Forecasting foundations (run: d15)",
            "D16  Ch16 Seasonality and baselines (run: d16)",
            "D17  Ch17 Revenue forecasting: segmentation + drivers (run: d17)",
            "D18  Ch18 Expense forecasting: fixed/variable/step + payroll (run: d18)",
            "D19  Ch19 Cash flow forecasting: direct method (13-week) (run: d19)",
            "D20  Ch20 Integrated forecasting: three statements (run: d20)",
            "D21  Ch21 Scenario planning: sensitivity + stress (run: d21)",
            "D22  Ch22 Financial statement analysis toolkit (run: d22)",
            "D23  Ch23 Communicating results and governance (run: d23)",
        ]
        print("\n".join(chapters))
        return 0

    # Track C (default): bundled in the starter zip.
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



def _workdir(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "workdir", ".")).expanduser().resolve()


_CHAPTER_RE: Final[re.Pattern[str]] = re.compile(r"^ch(?P<num>\d+)$", re.IGNORECASE)


def _chapter_num(key: str) -> int | None:
    m = _CHAPTER_RE.match(key.strip())
    if not m:
        return None
    return int(m.group("num"))


def _resolve_script_path(workdir: Path, target: str) -> Path:
    target = target.strip()

    # Explicit path?
    if target.endswith(".py") or "/" in target or "\\" in target:
        p = Path(target)
        if not p.is_absolute():
            p = workdir / p
        return p

    ch = _chapter_num(target)
    if ch is not None:
        return workdir / "scripts" / f"psych_ch{ch:02d}_problem_set.py"

    # Default: treat as a script key under scripts/
    return workdir / "scripts" / f"{target}.py"


def _resolve_test_path(workdir: Path, target: str) -> Path:
    target = target.strip()

    ch = _chapter_num(target)
    if ch is not None:
        return workdir / "tests" / f"test_psych_ch{ch:02d}_problem_set.py"

    # Try a few conventions for non-chapter keys.
    candidates = [
        workdir / "tests" / f"test_{target}.py",
        workdir / "tests" / f"test_{target}_case_study.py",
        workdir / "tests" / f"test_{target}_problem_set.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    # If none exist, still return the first candidate for a helpful error path.
    return candidates[0]


def cmd_workbook_run(args: argparse.Namespace) -> int:
    workdir = _workdir(args)
    script = _resolve_script_path(workdir, args.target)

    if not script.exists():
        print(
            "ERROR: Could not find the script to run.\n"
            f"   Looking for: {script}\n\n"
            "Tip: run this inside your workbook folder (created by `pystatsv1 workbook init`).\n"
            "     Or pass --workdir to point at it."
        )
        return 2

    # Ensure workbook-root imports like `import scripts.foo` work reliably.
    # Many workbook scripts use `from scripts...` imports; adding the workbook
    # directory to PYTHONPATH makes this consistent across platforms.
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    prefix = str(workdir)
    env["PYTHONPATH"] = (
        f"{prefix}{os.pathsep}{existing}" if existing else prefix
    )

    cmd = [sys.executable, str(script)]
    try:
        subprocess.run(cmd, cwd=str(workdir), env=env, check=True)
    except subprocess.CalledProcessError as e:
        return int(e.returncode or 1)
    return 0


def cmd_workbook_check(args: argparse.Namespace) -> int:
    workdir = _workdir(args)
    test_file = _resolve_test_path(workdir, args.target)

    if not test_file.exists():
        print(
            "ERROR: Could not find the test file to run.\n"
            f"   Looking for: {test_file}\n\n"
            "Tip: run this inside your workbook folder (created by `pystatsv1 workbook init`).\n"
            "     Or pass --workdir to point at it."
        )
        return 2

    # Match `workbook run`: keep workbook-root import resolution consistent.
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    prefix = str(workdir)
    env["PYTHONPATH"] = f"{prefix}{os.pathsep}{existing}" if existing else prefix

    cmd = [sys.executable, "-m", "pytest", "-q", str(test_file)]
    try:
        subprocess.run(cmd, cwd=str(workdir), env=env, check=True)
    except subprocess.CalledProcessError as e:
        return int(e.returncode or 1)
    return 0

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
            "WARNING: You are NOT in a virtual environment. This is OK, but not recommended.\n"
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
            "\nERROR: Missing packages in this environment:\n  - "
            + "\n  - ".join(missing)
            + "\n\nInstall the student bundle:\n"
            "  python -m pip install -U pip\n"
            "  python -m pip install \"pystatsv1[workbook]\"\n"
        )

    if ok:
        if in_venv:
            print("OK: Environment looks good.")
        else:
            print("OK: Packages look good (consider using a venv).")
        return 0

    return 1


def cmd_trackd_validate(args: argparse.Namespace) -> int:
    # Keep CLI wiring lightweight: validation logic lives in pystatsv1.trackd.validate.
    from pystatsv1.trackd import TrackDDataError, TrackDSchemaError
    from pystatsv1.trackd.validate import validate_dataset

    try:
        validate_dataset(args.datadir, profile=args.profile)
    except (TrackDDataError, TrackDSchemaError) as e:
        print(str(e))
        return 1

    print(
        textwrap.dedent(
            f"""\
            Track D dataset looks valid.

            Profile: {args.profile}
            Data directory: {Path(args.datadir).expanduser()}
            """
        ).rstrip()
    )
    return 0



def cmd_trackd_byod_init(args: argparse.Namespace) -> int:
    # Keep CLI wiring lightweight: creation logic lives in pystatsv1.trackd.byod.
    from pystatsv1.trackd import TrackDDataError
    from pystatsv1.trackd.byod import init_byod_project

    try:
        root = init_byod_project(args.dest, profile=args.profile, force=args.force)
    except TrackDDataError as e:
        print(str(e))
        return 1

    print(
        textwrap.dedent(
            f"""\
            Track D BYOD project created at:\n
                {root}\n
            Next steps:\n              1) cd {root}\n              2) Fill in the required CSVs in tables/\n              3) pystatsv1 trackd validate --datadir tables --profile {args.profile}\n            """
        ).rstrip()
    )
    return 0


def cmd_trackd_byod_normalize(args: argparse.Namespace) -> int:
    from pystatsv1.trackd import TrackDDataError, TrackDSchemaError
    from pystatsv1.trackd.byod import normalize_byod_project

    try:
        report = normalize_byod_project(args.project, profile=args.profile)
    except (TrackDDataError, TrackDSchemaError) as e:
        print(str(e))
        return 1

    files = report.get("files", [])
    written = "\n".join(f"  - {Path(f['dst']).name}" for f in files)

    print(
        textwrap.dedent(
            f"""\
            Track D BYOD normalization complete.

            Adapter: {report.get('adapter')}
            Profile: {report.get('profile')}
            Project: {report.get('project')}
            Input tables: {report.get('tables_dir')}
            Output normalized: {report.get('normalized_dir')}
            Wrote:\n{written}
            """
        ).rstrip()
    )
    return 0


def cmd_trackd_byod_daily_totals(args: argparse.Namespace) -> int:
    from pystatsv1.trackd import TrackDDataError
    from pystatsv1.trackd.byod import build_daily_totals

    try:
        report = build_daily_totals(args.project, out=args.out)
    except TrackDDataError as e:
        print(str(e))
        return 1

    print(
        textwrap.dedent(
            f"""\
            Track D BYOD daily totals written.

            Project: {report.get('project')}
            Output: {report.get('out')}
            Days: {report.get('days')}
            """
        ).rstrip()
    )
    return 0


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
        "--track",
        default="c",
        help="Which workbook to create: c (intro/psych) or d (business case). Default: c.",
    )
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

    p_list = wb_sub.add_parser("list", help="List chapters included in a starter kit.")
    p_list.add_argument(
        "--track",
        default="c",
        help="Which chapter list to show: c (intro/psych) or d (business case). Default: c.",
    )
    p_list.set_defaults(func=cmd_workbook_list)

    p_run = wb_sub.add_parser("run", help="Run a workbook script (no make required).")
    p_run.add_argument(
        "target",
        help="Target to run: chapter key like 'ch10', a script key like 'study_habits_01_explore', or a .py path.",
    )
    p_run.add_argument(
        "--workdir",
        default=".",
        help="Workbook directory (default: current directory).",
    )
    p_run.set_defaults(func=cmd_workbook_run)

    p_check = wb_sub.add_parser("check", help="Run workbook checks/tests via pytest (no make required).")
    p_check.add_argument(
        "target",
        help="Target to check: chapter key like 'ch10' or a key that resolves to tests/test_<key>*.py.",
    )
    p_check.add_argument(
        "--workdir",
        default=".",
        help="Workbook directory (default: current directory).",
    )
    p_check.set_defaults(func=cmd_workbook_check)

    p_trackd = sub.add_parser("trackd", help="Track D helpers (business datasets).")
    td_sub = p_trackd.add_subparsers(dest="trackd_cmd", required=True)

    p_td_validate = td_sub.add_parser(
        "validate",
        help="Validate a Track D dataset folder against a profile (BYOD foundations).",
    )
    p_td_validate.add_argument(
        "--datadir",
        required=True,
        help="Path to the folder containing exported Track D CSV tables.",
    )
    p_td_validate.add_argument(
        "--profile",
        default="full",
        choices=["core_gl", "ar", "full"],
        help="Which profile to validate (default: full).",
    )
    p_td_validate.set_defaults(func=cmd_trackd_validate)

    p_td_byod = td_sub.add_parser("byod", help="Bring-your-own-data (BYOD) project helpers.")
    byod_sub = p_td_byod.add_subparsers(dest="trackd_byod_cmd", required=True)

    p_byod_init = byod_sub.add_parser("init", help="Create a BYOD project folder with CSV header templates.")
    p_byod_init.add_argument(
        "--dest",
        default="pystatsv1_trackd_byod",
        help="Destination directory to create (default: pystatsv1_trackd_byod).",
    )
    p_byod_init.add_argument(
        "--profile",
        default="core_gl",
        choices=["core_gl", "ar", "full"],
        help="Which profile to scaffold (default: core_gl).",
    )
    p_byod_init.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing non-empty directory.",
    )
    p_byod_init.set_defaults(func=cmd_trackd_byod_init)

    p_byod_norm = byod_sub.add_parser(
        "normalize",
        help="Normalize BYOD tables/ into canonical normalized/ outputs (Phase 2 skeleton).",
    )
    p_byod_norm.add_argument(
        "--project",
        required=True,
        help="Path to a BYOD project folder created by 'pystatsv1 trackd byod init'.",
    )
    p_byod_norm.add_argument(
        "--profile",
        default=None,
        choices=["core_gl", "ar", "full"],
        help="Override profile (default: read from config.toml).",
    )
    p_byod_norm.set_defaults(func=cmd_trackd_byod_normalize)

    p_byod_daily = byod_sub.add_parser(
        "daily-totals",
        help="Compute daily revenue/expense proxies from normalized tables.",
    )
    p_byod_daily.add_argument(
        "--project",
        required=True,
        help="Path to a BYOD project folder created by 'pystatsv1 trackd byod init'.",
    )
    p_byod_daily.add_argument(
        "--out",
        default=None,
        help="Optional output CSV path (default: <project>/normalized/daily_totals.csv).",
    )
    p_byod_daily.set_defaults(func=cmd_trackd_byod_daily_totals)

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
