# SPDX-License-Identifier: MIT
"""Track D — Chapter 23: Communicating results (memos, dashboards, governance).

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* ch23_memo_template.md
* ch23_kpi_governance_template.csv
* ch23_dashboard_spec_template.csv
* ch23_red_team_checklist.md
* ch23_design.json

This chapter is intentionally **lightweight**. Instead of introducing new
statistics, it generates decision-ready *templates* that students can fill in
after running Chapters 18–22.

The goal: make analysis usable.

- A memo that answers: *what happened, why, what next, risks.*
- A KPI governance table so teams stop debating definitions.
- A dashboard spec so plots have owners, thresholds, and update cadence.

Data source: NSO v1 simulator outputs under a folder like ``data/synthetic/nso_v1``.

Outputs are deterministic and written under ``outputs/track_d``.

Guardrails
----------
- These templates are planning/communication tools.
- Any numbers we pre-fill are descriptive snapshots from the synthetic dataset.
- Avoid causal claims: "associated with" beats "caused by"."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser

CHAPTER = "Track D — Chapter 23"


@dataclass(frozen=True)
class Outputs:
    memo_template_md: Path
    kpi_governance_template_csv: Path
    dashboard_spec_template_csv: Path
    red_team_checklist_md: Path
    design_json: Path


def _read_statement(datadir: Path, name: str) -> pd.DataFrame:
    path = datadir / name
    if not path.exists():
        raise FileNotFoundError(f"Expected {name} at {path}, but it was not found.")
    df = pd.read_csv(path)
    # Expected schema from simulator: month, line, amount
    required = {"month", "line", "amount"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{name} missing required columns: {sorted(missing)}")
    return df


def _wide_by_line(df_long: pd.DataFrame, *, lines: list[str]) -> pd.DataFrame:
    if df_long.empty:
        return pd.DataFrame(columns=["month", *lines])

    df = df_long.copy()
    df["month"] = df["month"].astype(str)
    df["line"] = df["line"].astype(str)
    df = df[df["line"].isin(lines)].copy()

    wide = df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum", fill_value=0.0)
    wide = wide.reset_index().sort_values("month").reset_index(drop=True)
    for col in lines:
        if col not in wide.columns:
            wide[col] = 0.0
    return wide


def _safe_div(num: float, den: float) -> float:
    if den == 0.0:
        return float("nan")
    return float(num) / float(den)


def _fmt_currency(x: float) -> str:
    if not np.isfinite(x):
        return "(n/a)"
    return f"${x:,.2f}"


def _fmt_pct(x: float) -> str:
    if not np.isfinite(x):
        return "(n/a)"
    return f"{100.0 * x:,.1f}%"


def _fmt_days(x: float) -> str:
    if not np.isfinite(x):
        return "(n/a)"
    return f"{x:,.0f} days"


def _snapshot_metrics(*, is_wide: pd.DataFrame, bs_wide: pd.DataFrame) -> dict[str, Any]:
    """Compute a small "latest month" snapshot for pre-filling templates."""

    if len(is_wide) == 0 or len(bs_wide) == 0:
        return {
            "month": "(unknown)",
            "revenue": float("nan"),
            "net_income": float("nan"),
            "gross_margin": float("nan"),
            "operating_margin": float("nan"),
            "cash": float("nan"),
            "dso_days": float("nan"),
            "dio_days": float("nan"),
            "dpo_days": float("nan"),
            "ccc_days": float("nan"),
            "current_ratio": float("nan"),
            "quick_ratio": float("nan"),
        }

    # Align months (outer join, deterministic ordering)
    wide = is_wide.merge(bs_wide, on="month", how="outer")
    wide = wide.sort_values("month").reset_index(drop=True)
    last = wide.iloc[-1]

    rev = float(last.get("Sales Revenue", 0.0))
    cogs = float(last.get("Cost of Goods Sold", 0.0))
    net = float(last.get("Net Income", 0.0))

    cash = float(last.get("Cash", 0.0))
    ar = float(last.get("Accounts Receivable", 0.0))
    inv = float(last.get("Inventory", 0.0))
    ap = float(last.get("Accounts Payable", 0.0))
    stp = float(last.get("Sales Tax Payable", 0.0))
    wp = float(last.get("Wages Payable", 0.0))
    ptp = float(last.get("Payroll Taxes Payable", 0.0))

    gross_margin = _safe_div(rev - cogs, rev)
    operating_margin = _safe_div(net, rev)

    # Days approximations (month-level): AR / (rev/30), etc.
    dso = 30.0 * _safe_div(ar, _safe_div(rev, 30.0)) if rev != 0.0 else float("nan")
    dio = 30.0 * _safe_div(inv, _safe_div(cogs, 30.0)) if cogs != 0.0 else float("nan")
    dpo = 30.0 * _safe_div(ap, _safe_div(cogs, 30.0)) if cogs != 0.0 else float("nan")
    ccc = dso + dio - dpo if np.isfinite(dso) and np.isfinite(dio) and np.isfinite(dpo) else float("nan")

    current_assets = cash + ar + inv
    current_liabilities = ap + stp + wp + ptp
    current_ratio = _safe_div(current_assets, current_liabilities) if current_liabilities != 0.0 else float("nan")
    quick_ratio = _safe_div(cash + ar, current_liabilities) if current_liabilities != 0.0 else float("nan")

    return {
        "month": str(last.get("month", "(unknown)")),
        "revenue": rev,
        "net_income": net,
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "cash": cash,
        "dso_days": dso,
        "dio_days": dio,
        "dpo_days": dpo,
        "ccc_days": ccc,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
    }


def _kpi_governance_table() -> pd.DataFrame:
    """A governance starter table: definitions + ownership + thresholds."""

    # NOTE: Column names are part of the Track D contract (tests rely on them).
    cols = [
        "kpi_name",
        "definition",
        "formula",
        "source_table",
        "source_columns",
        "owner_role",
        "update_cadence",
        "threshold_green",
        "threshold_yellow",
        "threshold_red",
        "notes",
    ]

    rows: list[dict[str, Any]] = [
        {
            "kpi_name": "Revenue (monthly)",
            "definition": "Sales revenue for the month (accrual).",
            "formula": "Sales Revenue",
            "source_table": "statements_is_monthly.csv",
            "source_columns": "month,line_item,value (Sales Revenue)",
            "owner_role": "FP&A / Controller",
            "update_cadence": "Monthly close",
            "threshold_green": "(set by plan)",
            "threshold_yellow": "(set by plan)",
            "threshold_red": "(set by plan)",
            "notes": "Confirm revenue recognition policy; document one-offs.",
        },
        {
            "kpi_name": "Gross margin %",
            "definition": "Gross profit as a percent of revenue.",
            "formula": "(Revenue - COGS) / Revenue",
            "source_table": "statements_is_monthly.csv",
            "source_columns": "month,line_item,value (Sales Revenue, Cost of Goods Sold)",
            "owner_role": "FP&A / Controller",
            "update_cadence": "Monthly close",
            "threshold_green": ">= target",
            "threshold_yellow": "near target",
            "threshold_red": "below target",
            "notes": "Track price/volume/mix; validate inventory/COGS timing.",
        },
        {
            "kpi_name": "Operating margin %",
            "definition": "Net income as a percent of revenue (simplified).",
            "formula": "Net Income / Revenue",
            "source_table": "statements_is_monthly.csv",
            "source_columns": "month,line_item,value (Net Income, Sales Revenue)",
            "owner_role": "FP&A / Controller",
            "update_cadence": "Monthly close",
            "threshold_green": ">= target",
            "threshold_yellow": "near target",
            "threshold_red": "below target",
            "notes": "Separate one-offs; avoid causal over-claims.",
        },
        {
            "kpi_name": "Net income (monthly)",
            "definition": "Bottom-line profit for the month.",
            "formula": "Net Income",
            "source_table": "statements_is_monthly.csv",
            "source_columns": "month,line_item,value (Net Income)",
            "owner_role": "Controller",
            "update_cadence": "Monthly close",
            "threshold_green": "(set by plan)",
            "threshold_yellow": "(set by plan)",
            "threshold_red": "(set by plan)",
            "notes": "Review unusual items; link to variance explanations.",
        },
        {
            "kpi_name": "Cash balance",
            "definition": "Cash on hand at period end.",
            "formula": "Cash",
            "source_table": "statements_bs_monthly.csv",
            "source_columns": "month,line_item,value (Cash)",
            "owner_role": "Treasury / Controller",
            "update_cadence": "Weekly (rolling) + Month-end",
            "threshold_green": "> buffer",
            "threshold_yellow": "near buffer",
            "threshold_red": "below buffer",
            "notes": "Tie to bank reconciliation; define trigger thresholds.",
        },
        {
            "kpi_name": "Current ratio",
            "definition": "Short-term liquidity (current assets / current liabilities).",
            "formula": "(Cash + AR + Inventory) / (AP + sales tax payable + wages payable + payroll taxes payable)",
            "source_table": "statements_bs_monthly.csv",
            "source_columns": "month,line_item,value (Cash, Accounts Receivable, Inventory, Accounts Payable, Sales Tax Payable, Wages Payable, Payroll Taxes Payable)",
            "owner_role": "Controller",
            "update_cadence": "Monthly close",
            "threshold_green": ">= policy",
            "threshold_yellow": "watch",
            "threshold_red": "below policy",
            "notes": "Inventory quality matters; adjust for slow/obsolete stock if needed.",
        },
        {
            "kpi_name": "Quick ratio",
            "definition": "Liquidity excluding inventory (cash + AR) / current liabilities.",
            "formula": "(Cash + AR) / (AP + sales tax payable + wages payable + payroll taxes payable)",
            "source_table": "statements_bs_monthly.csv",
            "source_columns": "month,line_item,value (Cash, Accounts Receivable, Accounts Payable, Sales Tax Payable, Wages Payable, Payroll Taxes Payable)",
            "owner_role": "Controller",
            "update_cadence": "Monthly close",
            "threshold_green": ">= policy",
            "threshold_yellow": "watch",
            "threshold_red": "below policy",
            "notes": "Good for short-horizon cash risk; still validate AR collectability.",
        },
        {
            "kpi_name": "DSO (days)",
            "definition": "Days sales outstanding (collection speed; approximation).",
            "formula": "Accounts Receivable / (Revenue / 30)",
            "source_table": "statements_is_monthly.csv + statements_bs_monthly.csv",
            "source_columns": "month,line_item,value (Accounts Receivable, Sales Revenue)",
            "owner_role": "AR Lead / Controller",
            "update_cadence": "Monthly close",
            "threshold_green": "improving",
            "threshold_yellow": "flat",
            "threshold_red": "worsening",
            "notes": "Cross-check with AR aging; separate disputed invoices.",
        },
        {
            "kpi_name": "Cash conversion cycle (days)",
            "definition": "Approx. days cash is tied up in working capital.",
            "formula": "DSO + DIO - DPO (month-level approximation)",
            "source_table": "statements_is_monthly.csv + statements_bs_monthly.csv",
            "source_columns": "month,line_item,value (AR, Inventory, AP, Sales Revenue, COGS)",
            "owner_role": "Controller + Ops",
            "update_cadence": "Monthly close",
            "threshold_green": "improving",
            "threshold_yellow": "flat",
            "threshold_red": "worsening",
            "notes": "Directional metric; validate with AR/AP aging and inventory turns.",
        },
    ]

    return pd.DataFrame(rows, columns=cols)


def _dashboard_spec() -> pd.DataFrame:
    """A small dashboard spec: what to show, how, and why."""

    rows: list[dict[str, Any]] = [
        {
            "panel": "Performance",
            "metric": "Revenue",
            "chart": "line",
            "grain": "monthly",
            "owner": "FP&A",
            "decision": "Are we on plan?",
            "guardrail": "Use consistent time windows; annotate one-offs.",
        },
        {
            "panel": "Margins",
            "metric": "Gross margin %",
            "chart": "line",
            "grain": "monthly",
            "owner": "FP&A",
            "decision": "Is pricing/COGS behaving?",
            "guardrail": "Validate inventory/COGS; do not hide reclasses.",
        },
        {
            "panel": "Cash",
            "metric": "Cash balance",
            "chart": "line",
            "grain": "weekly/13-week",
            "owner": "Controller",
            "decision": "Do we need a cash action now?",
            "guardrail": "Tie to bank; make buffer trigger explicit.",
        },
        {
            "panel": "Working capital",
            "metric": "Cash conversion cycle (days)",
            "chart": "line",
            "grain": "monthly",
            "owner": "Controller + Ops",
            "decision": "Where is cash trapped?",
            "guardrail": "Directional only; validate AR/AP aging.",
        },
    ]
    return pd.DataFrame(rows)


def _memo_template(*, snapshot: dict[str, Any]) -> str:
    """Return a markdown executive memo template with a small pre-filled snapshot."""

    month = snapshot.get("month", "(unknown)")
    rev = _fmt_currency(float(snapshot.get("revenue", float("nan"))))
    net = _fmt_currency(float(snapshot.get("net_income", float("nan"))))
    cash = _fmt_currency(float(snapshot.get("cash", float("nan"))))
    gm = _fmt_pct(float(snapshot.get("gross_margin", float("nan"))))
    om = _fmt_pct(float(snapshot.get("operating_margin", float("nan"))))
    ccc = _fmt_days(float(snapshot.get("ccc_days", float("nan"))))
    dso = _fmt_days(float(snapshot.get("dso_days", float("nan"))))

    return (
        "# North Shore Outfitters — Executive Update (Template)\n\n"
        "**Audience:** CFO / Owner / Leadership\n\n"
        f"**Reporting period:** {month} (latest month in dataset)\n\n"
        "---\n\n"
        "## 1) What happened (facts)\n\n"
        "Write 3–6 bullet points that describe *what changed* without guessing why.\n\n"
        "**Snapshot (auto-filled from NSO synthetic data):**\n\n"
        f"- Revenue: {rev}\n"
        f"- Net income: {net}\n"
        f"- Cash (end of month): {cash}\n"
        f"- Gross margin: {gm}\n"
        f"- Operating margin: {om}\n"
        f"- DSO (approx): {dso}\n"
        f"- Cash conversion cycle (approx): {ccc}\n\n"
        "*(Replace this snapshot if you are using real data.)*\n\n"
        "## 2) Why it happened (drivers, not blame)\n\n"
        "Use one of these driver frames (pick 1–2):\n\n"
        "- **Price / Volume / Mix** (revenue or gross margin)\n"
        "- **Cost behavior** (fixed vs variable vs step costs)\n"
        "- **Working capital** (AR collections, inventory, AP timing)\n\n"
        "**Guardrail:** If you cannot rule out confounders, say \"associated with\" instead of \"caused by\".\n\n"
        "## 3) What we recommend next (actions + owners)\n\n"
        "List 3–5 actions. Each action must have: **owner, due date, expected impact range**.\n\n"
        "| Action | Owner | When | Expected impact | KPI to monitor |\n"
        "|---|---|---|---|---|\n"
        "|  |  |  |  |  |\n\n"
        "## 4) Risks & uncertainty (don’t hide it)\n\n"
        "- Biggest downside risks\n"
        "- Early warning indicators\n"
        "- Contingency plan (if worst-case scenario triggers)\n\n"
        "## 5) Assumptions & audit trail\n\n"
        "- Data sources used\n"
        "- One-off adjustments (what, why, who approved)\n"
        "- Version / run-id / links to artifacts\n\n"
        "## 6) Governance\n\n"
        "- Update cadence (weekly cash, monthly close)\n"
        "- Who approves forecast changes\n"
        "- Where templates and outputs live (shared folder / repo)\n"
    )


def _red_team_checklist() -> str:
    return (
        "# Chapter 23 — Red team checklist (avoid overclaiming)\n\n"
        "Use this list to critique your own memo/dashboard before sharing it.\n\n"
        "## Interpretation guardrails\n\n"
        "- Did we accidentally imply causation from correlation?\n"
        "- Did we ignore seasonality, one-offs, or timing effects?\n"
        "- Are we comparing like-for-like periods (same days, same cutoff)?\n\n"
        "## Data quality guardrails\n\n"
        "- Are bank rec / AR/AP ties / exception checks complete?\n"
        "- Are reclasses documented and approved?\n"
        "- Are definitions consistent with the KPI governance table?\n\n"
        "## Communication guardrails\n\n"
        "- Are actions specific (owner + due date + KPI)?\n"
        "- Did we quantify impact as a range, not a single point?\n"
        "- Is uncertainty clearly stated without being vague?\n"
    )


def analyze_ch23(*, datadir: Path, outdir: Path, seed: int | None = None) -> Outputs:
    apply_seed(seed)

    outdir.mkdir(parents=True, exist_ok=True)

    is_df = _read_statement(datadir, "statements_is_monthly.csv")
    bs_df = _read_statement(datadir, "statements_bs_monthly.csv")

    is_lines = ["Sales Revenue", "Cost of Goods Sold", "Operating Expenses", "Net Income"]
    bs_lines = [
        "Cash",
        "Accounts Receivable",
        "Inventory",
        "Accounts Payable",
        "Sales Tax Payable",
        "Wages Payable",
        "Payroll Taxes Payable",
    ]

    is_wide = _wide_by_line(is_df, lines=is_lines)
    bs_wide = _wide_by_line(bs_df, lines=bs_lines)

    snapshot = _snapshot_metrics(is_wide=is_wide, bs_wide=bs_wide)

    memo_template_md = outdir / "ch23_memo_template.md"
    memo_template_md.write_text(_memo_template(snapshot=snapshot), encoding="utf-8")

    kpi_governance_template_csv = outdir / "ch23_kpi_governance_template.csv"
    _kpi_governance_table().to_csv(kpi_governance_template_csv, index=False)

    dashboard_spec_template_csv = outdir / "ch23_dashboard_spec_template.csv"
    _dashboard_spec().to_csv(dashboard_spec_template_csv, index=False)

    red_team_checklist_md = outdir / "ch23_red_team_checklist.md"
    red_team_checklist_md.write_text(_red_team_checklist(), encoding="utf-8")

    design_json = outdir / "ch23_design.json"
    design: dict[str, Any] = {
        "chapter": CHAPTER,
        "seed": seed,
        "datadir": str(datadir).replace("\\\\", "/"),
        "outdir": str(outdir).replace("\\\\", "/"),
        "artifacts": [
            memo_template_md.name,
            kpi_governance_template_csv.name,
            dashboard_spec_template_csv.name,
            red_team_checklist_md.name,
        ],
        "snapshot": {
            "month": snapshot.get("month"),
            "revenue": float(snapshot.get("revenue", float("nan"))),
            "net_income": float(snapshot.get("net_income", float("nan"))),
            "cash": float(snapshot.get("cash", float("nan"))),
            "gross_margin": float(snapshot.get("gross_margin", float("nan"))),
            "operating_margin": float(snapshot.get("operating_margin", float("nan"))),
        },
        "guardrails": [
            "Do not overclaim causality; prefer 'associated with'.",
            "Document reclasses and one-offs in an assumptions log.",
            "Tie cash numbers to a bank reconciliation.",
        ],
    }
    design_json.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return Outputs(
        memo_template_md=memo_template_md,
        kpi_governance_template_csv=kpi_governance_template_csv,
        dashboard_spec_template_csv=dashboard_spec_template_csv,
        red_team_checklist_md=red_team_checklist_md,
        design_json=design_json,
    )


def main(argv: list[str] | None = None) -> None:
    p = base_parser(description=f"{CHAPTER}: communication + governance templates")
    p.add_argument(
        "--datadir",
        type=Path,
        default=Path("data/synthetic/nso_v1"),
        help="Directory containing NSO v1 synthetic tables (default: data/synthetic/nso_v1)",
    )
    args = p.parse_args(argv)

    out = analyze_ch23(datadir=args.datadir, outdir=args.outdir, seed=args.seed)
    print(f"Wrote Chapter 23 artifacts -> {out.design_json.parent}")


if __name__ == "__main__":
    main()
