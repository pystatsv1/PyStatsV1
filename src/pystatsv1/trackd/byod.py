# SPDX-License-Identifier: MIT
"""Bring-your-own-data (BYOD) helpers for Track D.

Phase 2 foundation:
- create a local BYOD project folder
- generate header-only CSV templates from the canonical Track D contracts

Design: avoid shipping a second "header pack" contract.
We generate templates directly from :mod:`pystatsv1.trackd.schema` so the
single source of truth stays in one place.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import textwrap
from pathlib import Path
from typing import Any

from ._errors import TrackDDataError, TrackDSchemaError
from ._types import PathLike
from .adapters.base import NormalizeContext, TrackDAdapter
from .contracts import ALLOWED_PROFILES, schemas_for_profile


def _read_trackd_config(project_root: Path) -> dict[str, str]:
    """Read a tiny subset of config.toml.

    The BYOD config is intentionally minimal (and write-only in the early PRs).
    We parse just enough here to support normalization:

    - [trackd].profile
    - [trackd].tables_dir
    - [trackd].adapter

    Notes
    -----
    - We avoid adding a TOML dependency (Python 3.10).
    - Unknown keys are ignored.
    """

    cfg_path = project_root / "config.toml"
    if not cfg_path.exists():
        return {}

    section: str | None = None
    out: dict[str, str] = {}

    for raw in cfg_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]").strip()
            continue
        if section != "trackd" or "=" not in line:
            continue

        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        if key in {"profile", "tables_dir", "adapter"}:
            out[key] = val

    return out


def _normalize_csv(
    src: Path, dst: Path, *, required_columns: tuple[str, ...]
) -> dict[str, Any]:
    """Write a normalized CSV with canonical column order.

    - required columns appear first, in contract order
    - any extra columns are preserved, appended in their original order
    """

    with src.open("r", newline="", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            # This should be caught by validate(), but keep a friendly message.
            raise TrackDDataError(f"CSV appears to have no header row: {src.name}")

        fieldnames = [str(c) for c in reader.fieldnames if c is not None]
        required = list(required_columns)
        required_set = set(required)
        extras = [c for c in fieldnames if c not in required_set]
        out_fields = required + extras

        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fields)
            writer.writeheader()
            n_rows = 0
            for row in reader:
                out_row = {k: (row.get(k) or "") for k in out_fields}
                writer.writerow(out_row)
                n_rows += 1

    return {
        "src": str(src),
        "dst": str(dst),
        "written_rows": n_rows,
        "written_columns": out_fields,
    }


def init_byod_project(dest: PathLike, *, profile: str = "core_gl", force: bool = False) -> Path:
    """Create a Track D BYOD project folder.

    The project layout is intentionally simple:

    - tables/      student-edited CSVs (header templates created here)
    - raw/         optional dumps from source systems
    - normalized/  adapter outputs (generated)
    - notes/       assumptions, mapping notes, and QA

    Parameters
    ----------
    dest:
        Destination folder to create.
    profile:
        One of: core_gl, ar, full.
    force:
        Allow writing into an existing non-empty directory.

    Returns
    -------
    Path
        The created project root.

    Raises
    ------
    TrackDDataError
        If *dest* is non-empty and *force* is False, or if *profile* is invalid.
    """

    root = Path(dest).expanduser().resolve()

    if root.exists() and any(root.iterdir()) and not force:
        raise TrackDDataError(
            f"Refusing to write into non-empty directory: {root}\n"
            "Use --force to overwrite into an existing directory."
        )

    p = (profile or "").strip().lower()
    try:
        schemas = schemas_for_profile(p)
    except ValueError as e:
        raise TrackDDataError(
            f"Unknown profile: {profile}.\n" f"Use one of: {', '.join(ALLOWED_PROFILES)}"
        ) from e

    # Create core folders
    root.mkdir(parents=True, exist_ok=True)
    (root / "tables").mkdir(parents=True, exist_ok=True)
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "normalized").mkdir(parents=True, exist_ok=True)
    (root / "notes").mkdir(parents=True, exist_ok=True)

    # Write header-only CSV templates into tables/
    for schema in schemas:
        out = root / "tables" / schema.name
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(list(schema.required_columns))

    # Tiny config (write-only for now)
    config = textwrap.dedent(
        f"""\
        # Track D BYOD project config
        [trackd]
        profile = "{p}"
        tables_dir = "tables"
        adapter = "passthrough"
        """
    ).lstrip()
    (root / "config.toml").write_text(config, encoding="utf-8")

    readme = textwrap.dedent(
        f"""\
        # Track D — Bring Your Own Data (BYOD)

        This folder is a starter project for using your own accounting data with Track D.

        ## What to edit

        - `tables/` contains **student-edited** CSVs.
          Header-only templates are generated from the Track D contract.

        ## What not to edit

        - `normalized/` is for **generated** outputs from future adapters.

        ## Quickstart

        1) Fill in the required CSVs under `tables/`.
        2) Validate your dataset:

           ```bash
           pystatsv1 trackd validate --datadir tables --profile {p}
           ```

        If validation fails, fix the missing files/columns and re-run.
        """
    ).lstrip()

    (root / "README.md").write_text(readme, encoding="utf-8")
    return root


class _PassthroughAdapter:
    """Sheets-first adapter: treat tables/ as already canonical.

    Normalization for this adapter means:
    - enforce required headers exist (handled before calling the adapter)
    - write out normalized/*.csv with contract column ordering
    - preserve any extra columns (appended)
    """

    name = "passthrough"

    def normalize(self, ctx: NormalizeContext) -> dict[str, Any]:
        schemas = schemas_for_profile(ctx.profile)
        ctx.normalized_dir.mkdir(parents=True, exist_ok=True)

        files: list[dict[str, Any]] = []
        for schema in schemas:
            src = ctx.tables_dir / schema.name
            dst = ctx.normalized_dir / schema.name
            files.append(_normalize_csv(src, dst, required_columns=schema.required_columns))

        return {
            "ok": True,
            "adapter": self.name,
            "profile": ctx.profile,
            "project": str(ctx.project_root),
            "tables_dir": str(ctx.tables_dir),
            "normalized_dir": str(ctx.normalized_dir),
            "files": files,
        }


def _get_adapter(name: str | None) -> TrackDAdapter:
    n = (name or "").strip().lower() or "passthrough"
    if n == "passthrough":
        return _PassthroughAdapter()
    if n == "core_gl":
        from .adapters.core_gl import CoreGLAdapter

        return CoreGLAdapter()
    if n == "gnucash_gl":
        from .adapters.gnucash_gl import GnuCashGLAdapter

        return GnuCashGLAdapter()
    raise TrackDDataError(
        f"Unknown adapter: {name}.\n" "Use one of: passthrough, core_gl, gnucash_gl"
    )



def normalize_byod_project(project: PathLike, *, profile: str | None = None) -> dict[str, Any]:
    """Normalize BYOD project tables into ``normalized/`` outputs.

    This is a *Phase 2 skeleton* implementation:
    - validates required files + required columns (headers)
    - re-writes CSVs in canonical contract column order

    Parameters
    ----------
    project:
        BYOD project root (created by :func:`init_byod_project`).
    profile:
        Optional override. If omitted, uses ``config.toml``.

    Returns
    -------
    dict
        Report dict with keys: ok, adapter, profile, project, tables_dir, normalized_dir, files.
    """

    from .validate import validate_dataset

    root = Path(project).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise TrackDDataError(f"Project directory not found: {root}")

    cfg = _read_trackd_config(root)
    p = (profile or cfg.get("profile") or "").strip().lower()
    if not p:
        raise TrackDDataError(
            f"Missing profile for BYOD project: {root}\n"
            "Fix: pass --profile <core_gl|ar|full> or create the project with 'pystatsv1 trackd byod init'."
        )

    tables_rel = cfg.get("tables_dir", "tables")
    tables_dir = (root / tables_rel).resolve()
    if not tables_dir.exists() or not tables_dir.is_dir():
        raise TrackDDataError(
            f"Tables directory not found: {tables_dir}\n"
            "Hint: your BYOD project should contain a 'tables/' folder."
        )

    adapter = _get_adapter(cfg.get("adapter"))

    # Validation strategy:
    # - passthrough expects contract-shaped inputs under tables/
    # - other adapters may accept non-canonical headers, so we validate after normalize
    if getattr(adapter, "name", "") == "passthrough":
        # Validate required schema issues first, so passthrough can assume headers exist.
        validate_dataset(tables_dir, profile=p)
    else:
        # Light check: required files must exist; detailed schema validation runs on normalized outputs.
        schemas = schemas_for_profile(p)
        missing = [s.name for s in schemas if not (tables_dir / s.name).exists()]
        if missing:
            raise TrackDSchemaError(
                "Missing required files in tables/: " + ", ".join(missing)
            )

    ctx = NormalizeContext(
        project_root=root,
        profile=p,
        tables_dir=tables_dir,
        raw_dir=(root / "raw"),
        normalized_dir=(root / "normalized"),
    )
    report = adapter.normalize(ctx)

    if getattr(adapter, "name", "") != "passthrough":
        # Ensure adapter output conforms to the Track D contract.
        validate_dataset(ctx.normalized_dir, profile=p)

    return report


# --- Phase 3 helper: daily totals from normalized GL ---

def _parse_decimal_money(value: str) -> Decimal:
    """Parse a money-like string into a Decimal.

    Notes
    -----
    - Accepts blanks and treats them as zero.
    - Strips commas so values like "1,234.56" work.
    """

    raw = (value or "").strip()
    if raw == "":
        return Decimal("0")

    cleaned = raw.replace(",", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise TrackDDataError(f"Invalid money amount: {value!r}") from exc


def _fmt_2dp(x: Decimal) -> str:
    q = x.quantize(Decimal("0.01"))
    return f"{q:.2f}"


def build_daily_totals(project: PathLike, *, out: PathLike | None = None) -> dict[str, Any]:
    """Compute daily revenue/expense proxies from normalized Track D tables.

    This helper is designed for students using **pip-installed** PyStatsV1.
    It turns:

    - normalized/gl_journal.csv
    - normalized/chart_of_accounts.csv

    into a small analysis-ready table:

    - date
    - revenue_proxy   (net credits to Revenue accounts)
    - expenses_proxy  (net debits to Expense accounts)
    - net_proxy       (revenue_proxy - expenses_proxy)

    Parameters
    ----------
    project:
        BYOD project root (created by ``pystatsv1 trackd byod init``).
    out:
        Optional output CSV path. Default: ``<project>/normalized/daily_totals.csv``.

    Returns
    -------
    dict
        Report with keys: ok, project, out, days, rows.
    """

    root = Path(project).expanduser().resolve()
    normalized = root / "normalized"
    gl_path = normalized / "gl_journal.csv"
    coa_path = normalized / "chart_of_accounts.csv"

    if not gl_path.exists():
        raise TrackDDataError(
            f"Missing normalized/gl_journal.csv under: {root}\n"
            "Run: pystatsv1 trackd byod normalize --project <project>"
        )
    if not coa_path.exists():
        raise TrackDDataError(
            f"Missing normalized/chart_of_accounts.csv under: {root}\n"
            "Run: pystatsv1 trackd byod normalize --project <project>"
        )

    # Map account_id -> account_type
    acct_type: dict[str, str] = {}
    with coa_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            aid = (row.get("account_id") or "").strip()
            at = (row.get("account_type") or "").strip()
            if aid:
                acct_type[aid] = at

    rev_by_date: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    exp_by_date: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    with gl_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = (row.get("date") or "").strip()
            if not date:
                continue

            aid = (row.get("account_id") or "").strip()
            at = acct_type.get(aid, "")

            debit = _parse_decimal_money(row.get("debit") or "")
            credit = _parse_decimal_money(row.get("credit") or "")

            if at == "Revenue":
                # Revenue is credit-normal; net revenue is credits minus debits.
                rev_by_date[date] += credit - debit
            elif at == "Expense":
                # Expenses are debit-normal; net expense is debits minus credits.
                exp_by_date[date] += debit - credit

    out_path = Path(out).expanduser().resolve() if out else (normalized / "daily_totals.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dates = sorted(set(rev_by_date) | set(exp_by_date))

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=("date", "revenue_proxy", "expenses_proxy", "net_proxy"),
        )
        writer.writeheader()
        rows = 0
        for d in dates:
            r = rev_by_date.get(d, Decimal("0"))
            e = exp_by_date.get(d, Decimal("0"))
            writer.writerow(
                {
                    "date": d,
                    "revenue_proxy": _fmt_2dp(r),
                    "expenses_proxy": _fmt_2dp(e),
                    "net_proxy": _fmt_2dp(r - e),
                }
            )
            rows += 1

    return {
        "ok": True,
        "project": str(root),
        "out": str(out_path),
        "days": len(dates),
        "rows": rows,
    }
