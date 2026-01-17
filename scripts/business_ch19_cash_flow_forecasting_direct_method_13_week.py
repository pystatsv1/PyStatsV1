# SPDX-License-Identifier: MIT
"""Track D — Chapter 19: Cash flow forecasting (direct method, 13-week).

This chapter builds a short-term cash forecast using a **direct method** view:

    cash receipts (inflows)  -  cash payments (outflows)  =  net cash flow

The NSO v1 simulator provides enough structure to demonstrate a realistic, accountant-friendly
workflow:

- Use the **bank statement feed** as the cash source of truth (timing matters).
- Use AR/AP/payroll/sales tax/debt events to explain (and stress test) working-capital timing.

Outputs are deterministic and written under outputs/track_d/.

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser
from scripts._reporting_style import FigureManifestRow, FigureSpec, plot_time_series, save_figure, style_context

CHAPTER = "Track D — Chapter 19"


@dataclass(frozen=True)
class Outputs:
    cash_history_weekly_csv: Path
    cash_forecast_13w_scenarios_csv: Path
    cash_assumptions_csv: Path
    cash_governance_template_csv: Path
    design_json: Path
    memo_md: Path
    figures_manifest_csv: Path


def _week_start_monday(dt: pd.Timestamp) -> pd.Timestamp:
    # Monday = 0
    return (dt - pd.Timedelta(days=int(dt.weekday()))).normalize()


def _classify_bank_txn(description: str, amount: float) -> str:
    d = str(description).lower()

    # Receipts
    if "cash sale" in d:
        return "cash_sales"
    if "collect on accounts receivable" in d:
        return "ar_collections"
    if "owner contribution" in d:
        return "owner_contribution"
    if "borrow" in d or "loan origination" in d:
        return "borrowings"

    # Payments
    if "pay accounts payable" in d:
        return "ap_payments"
    if "inventory purchase (cash" in d or "inventory purchase (cash)" in d:
        return "inventory_cash_purchase"
    if "pay monthly rent" in d:
        return "rent"
    if "pay utilities" in d:
        return "utilities"
    if "pay prior-month net wages" in d:
        return "payroll_net_wages"
    if "remit prior-month payroll taxes" in d:
        return "payroll_tax_remit"
    if "remit prior-month sales tax" in d:
        return "sales_tax_remit"
    if "pay note payable" in d:
        return "debt_payment"
    if "owner draw" in d:
        return "owner_draw"
    if "acquire fixed asset" in d:
        return "capex"

    return "other_receipts" if float(amount) > 0 else "other_payments"


def _build_history_weekly(bank_statement: pd.DataFrame) -> pd.DataFrame:
    if bank_statement.empty:
        return pd.DataFrame(
            columns=[
                "week_start",
                "cash_in_total",
                "cash_out_total",
                "net_cash_flow",
                "ending_cash",
            ]
        )

    df = bank_statement.copy()
    df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce")
    df = df.dropna(subset=["posted_date"]).copy()
    df["week_start"] = df["posted_date"].apply(_week_start_monday)
    df["category"] = [
        _classify_bank_txn(desc, amt) for desc, amt in zip(df["description"].astype(str), df["amount"].astype(float))
    ]

    # Aggregate signed amounts per week/category
    wk_cat = (
        df.groupby(["week_start", "category"], observed=True)["amount"].sum().reset_index().sort_values("week_start")
    )

    # Wide category view (signed amounts)
    wide = wk_cat.pivot_table(index="week_start", columns="category", values="amount", aggfunc="sum", fill_value=0.0)
    wide = wide.reset_index().sort_values("week_start").reset_index(drop=True)

    # Totals
    amt_cols = [c for c in wide.columns if c != "week_start"]
    wide["cash_in_total"] = wide[amt_cols].clip(lower=0.0).sum(axis=1)
    wide["cash_out_total"] = (-wide[amt_cols].clip(upper=0.0)).sum(axis=1)
    wide["net_cash_flow"] = wide[amt_cols].sum(axis=1)

    # Running cash balance (start at 0; bank statement includes initial capital)
    wide["ending_cash"] = wide["net_cash_flow"].cumsum()

    # Friendly ISO date labels
    wide["week_start"] = wide["week_start"].dt.strftime("%Y-%m-%d")
    return wide


def _buffer_target_from_history(history: pd.DataFrame) -> float:
    """Simple buffer policy: target covers a "bad" week.

    We use the 90th percentile of weekly cash outflows on weeks where net cash flow is negative.
    If there are no negative weeks (rare), fall back to the 75th percentile of total outflow.

    """
    if history.empty:
        return 0.0

    net = history["net_cash_flow"].astype(float)
    out = history["cash_out_total"].astype(float)

    bad = (-net.loc[net < 0]).astype(float)
    if len(bad) >= 3:
        return float(np.quantile(bad, 0.90))
    if len(out) >= 3:
        return float(np.quantile(out, 0.75))
    return float(out.mean())


def _seasonal_pattern_by_week_of_month(history: pd.DataFrame) -> pd.DataFrame:
    """Compute mean signed amount by (category, week_of_month) from recent history."""
    if history.empty:
        return pd.DataFrame(columns=["category", "week_of_month", "mean_amount"])

    # Identify category columns (everything except these)
    reserved = {"week_start", "cash_in_total", "cash_out_total", "net_cash_flow", "ending_cash"}
    cat_cols = [c for c in history.columns if c not in reserved]

    # long form
    long = history[["week_start", *cat_cols]].copy()
    long["week_start"] = pd.to_datetime(long["week_start"])
    long["week_of_month"] = 1 + ((long["week_start"].dt.day - 1) // 7)

    melted = long.melt(id_vars=["week_start", "week_of_month"], var_name="category", value_name="amount")

    pat = (
        melted.groupby(["category", "week_of_month"], observed=True)["amount"]
        .mean()
        .reset_index()
        .rename(columns={"amount": "mean_amount"})
    )
    return pat


def _baseline_amount(pattern: pd.DataFrame, overall_means: dict[str, float], category: str, week_of_month: int) -> float:
    hit = pattern.loc[(pattern["category"] == category) & (pattern["week_of_month"] == week_of_month)]
    if not hit.empty:
        return float(hit.iloc[0]["mean_amount"])
    return float(overall_means.get(category, 0.0))


def analyze_ch19(*, datadir: Path, outdir: Path, seed: int = 123) -> Outputs:
    """Run Chapter 19 analysis and write deterministic artifacts."""
    apply_seed(seed)

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    bank_statement_csv = Path(datadir) / "bank_statement.csv"
    ar_events_csv = Path(datadir) / "ar_events.csv"
    ap_events_csv = Path(datadir) / "ap_events.csv"

    bank = pd.read_csv(bank_statement_csv) if bank_statement_csv.exists() else pd.DataFrame()
    ar = pd.read_csv(ar_events_csv) if ar_events_csv.exists() else pd.DataFrame()
    ap = pd.read_csv(ap_events_csv) if ap_events_csv.exists() else pd.DataFrame()

    # -------------------------------
    # 1) Weekly cash history from bank feed
    # -------------------------------
    hist = _build_history_weekly(bank)

    cash_history_weekly_csv = outdir / "ch19_cash_history_weekly.csv"
    hist.to_csv(cash_history_weekly_csv, index=False)

    # -------------------------------
    # 2) Forecast scaffolding (13 weeks)
    # -------------------------------
    scenarios = ["Base", "Stress_Delayed_Collections", "Stress_Supplier_Terms_Tighten"]

    # Pattern window: use up to last 52 weeks for seasonality by week-of-month
    if not hist.empty:
        hist_recent = hist.tail(min(len(hist), 52)).copy()
    else:
        hist_recent = hist.copy()

    pattern = _seasonal_pattern_by_week_of_month(hist_recent)

    reserved = {"week_start", "cash_in_total", "cash_out_total", "net_cash_flow", "ending_cash"}
    categories = [c for c in hist.columns if c not in reserved]
    overall_means = {c: float(hist_recent[c].astype(float).mean()) for c in categories}

    # Forecast weeks
    if hist.empty:
        last_week = pd.Timestamp("2025-01-06")
        start_cash = 0.0
    else:
        last_week = pd.to_datetime(hist["week_start"].iloc[-1])
        start_cash = float(hist["ending_cash"].iloc[-1])

    forecast_weeks = [last_week + pd.Timedelta(days=7 * i) for i in range(1, 14)]

    buffer_target = _buffer_target_from_history(hist_recent)

    # Build baseline (signed amounts per category) by applying week-of-month pattern
    base_rows: list[dict[str, Any]] = []
    for wk in forecast_weeks:
        wom = int(1 + ((wk.day - 1) // 7))
        row: dict[str, Any] = {"week_start": wk.strftime("%Y-%m-%d"), "week_of_month": wom}
        for cat in categories:
            row[cat] = _baseline_amount(pattern, overall_means, cat, wom)
        base_rows.append(row)

    base_weekly = pd.DataFrame(base_rows)

    # Scenario adjustments
    def _apply_delayed_collections(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "ar_collections" not in out.columns:
            return out
        shifted = out["ar_collections"].astype(float) * 0.20
        out["ar_collections"] = out["ar_collections"].astype(float) * 0.80
        # push 20% two weeks later (within horizon)
        for i in range(len(out)):
            j = i + 2
            if j < len(out):
                out.loc[j, "ar_collections"] = float(out.loc[j, "ar_collections"] + shifted.iloc[i])
        return out

    def _apply_supplier_tighten(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for cat in ["ap_payments", "inventory_cash_purchase"]:
            if cat in out.columns:
                out[cat] = out[cat].astype(float) * 1.15
        return out

    scenario_frames: dict[str, pd.DataFrame] = {
        "Base": base_weekly,
        "Stress_Delayed_Collections": _apply_delayed_collections(base_weekly),
        "Stress_Supplier_Terms_Tighten": _apply_supplier_tighten(base_weekly),
    }

    # Assemble forecast table with running cash balances
    forecast_rows: list[dict[str, Any]] = []
    for scen in scenarios:
        scen_df = scenario_frames[scen].copy()
        scen_df = scen_df.sort_values("week_start").reset_index(drop=True)

        begin_cash = start_cash
        for _, r in scen_df.iterrows():
            # signed category amounts
            signed_sum = 0.0
            cash_in = 0.0
            cash_out = 0.0
            for cat in categories:
                amt = float(r.get(cat, 0.0))
                signed_sum += amt
                if amt >= 0:
                    cash_in += amt
                else:
                    cash_out += -amt

            end_cash = float(begin_cash + signed_sum)
            trigger = bool(end_cash < buffer_target)

            row_out: dict[str, Any] = {
                "week_start": str(r["week_start"]),
                "scenario": scen,
                "beginning_cash": float(begin_cash),
                "cash_in_total": float(cash_in),
                "cash_out_total": float(cash_out),
                "net_cash_flow": float(signed_sum),
                "ending_cash": float(end_cash),
                "buffer_target": float(buffer_target),
                "buffer_trigger": trigger,
            }
            # Optional: include the two key working-capital drivers as explicit columns when present
            if "ar_collections" in categories:
                row_out["cash_in_ar_collections"] = float(max(0.0, float(r.get("ar_collections", 0.0))))
            if "ap_payments" in categories:
                ap_amt = float(r.get("ap_payments", 0.0))
                row_out["cash_out_ap_payments"] = float(-ap_amt if ap_amt < 0 else 0.0)

            forecast_rows.append(row_out)
            begin_cash = end_cash

    fc = pd.DataFrame(forecast_rows)

    # Ensure stable ordering
    fc["week_start"] = pd.to_datetime(fc["week_start"])
    fc = fc.sort_values(["scenario", "week_start"], kind="mergesort").reset_index(drop=True)
    fc["week_start"] = fc["week_start"].dt.strftime("%Y-%m-%d")

    cash_forecast_13w_scenarios_csv = outdir / "ch19_cash_forecast_13w_scenarios.csv"
    fc.to_csv(cash_forecast_13w_scenarios_csv, index=False)

    # -------------------------------
    # 3) Assumptions + governance templates
    # -------------------------------
    # Simple AR/AP behavior summaries (for the story)
    def _safe_ratio(n: float, d: float) -> float:
        return float(n / d) if abs(d) > 1e-12 else 0.0

    ar_collect_rate = 0.0
    if not ar.empty and {"event_type", "cash_received", "amount"}.issubset(set(ar.columns)):
        inv_amt = float(ar.loc[ar["event_type"].astype(str) == "invoice", "amount"].sum())
        coll_amt = float(ar.loc[ar["event_type"].astype(str) == "collection", "cash_received"].sum())
        ar_collect_rate = _safe_ratio(coll_amt, inv_amt)

    ap_pay_rate = 0.0
    if not ap.empty and {"event_type", "cash_paid", "amount"}.issubset(set(ap.columns)):
        inv_amt = float(ap.loc[ap["event_type"].astype(str) == "invoice", "amount"].sum())
        pay_amt = float(ap.loc[ap["event_type"].astype(str) == "payment", "cash_paid"].sum())
        ap_pay_rate = _safe_ratio(pay_amt, inv_amt)

    assumptions_rows: list[dict[str, Any]] = []
    for scen in scenarios:
        assumptions_rows.extend(
            [
                {
                    "scenario": scen,
                    "assumption_key": "pattern_window_weeks",
                    "assumption_value": int(min(len(hist), 52)) if not hist.empty else 0,
                    "unit": "weeks",
                    "note": "Uses recent history to preserve timing patterns by week-of-month.",
                },
                {
                    "scenario": scen,
                    "assumption_key": "ar_collection_rate_history",
                    "assumption_value": float(ar_collect_rate),
                    "unit": "ratio",
                    "note": "History-based AR cash collections / invoices (teaching simplification).",
                },
                {
                    "scenario": scen,
                    "assumption_key": "ap_payment_rate_history",
                    "assumption_value": float(ap_pay_rate),
                    "unit": "ratio",
                    "note": "History-based AP cash paid / credit invoices (teaching simplification).",
                },
                {
                    "scenario": scen,
                    "assumption_key": "buffer_target",
                    "assumption_value": float(buffer_target),
                    "unit": "currency",
                    "note": "Target cash buffer based on recent distribution of weekly outflows.",
                },
            ]
        )

        if scen == "Stress_Delayed_Collections":
            assumptions_rows.append(
                {
                    "scenario": scen,
                    "assumption_key": "delayed_collections_shift",
                    "assumption_value": "20% shifted by +2 weeks",
                    "unit": "text",
                    "note": "Stress: some customers pay later than expected.",
                }
            )
        if scen == "Stress_Supplier_Terms_Tighten":
            assumptions_rows.append(
                {
                    "scenario": scen,
                    "assumption_key": "supplier_cash_out_multiplier",
                    "assumption_value": 1.15,
                    "unit": "multiplier",
                    "note": "Stress: suppliers require more cash / faster payment behavior.",
                }
            )

    cash_assumptions_csv = outdir / "ch19_cash_assumptions.csv"
    pd.DataFrame(assumptions_rows).to_csv(cash_assumptions_csv, index=False)

    governance = pd.DataFrame(
        [
            {
                "item": "Update cadence",
                "description": "Update the 13-week forecast weekly (after bank download).",
                "owner_role": "Bookkeeper / Controller",
                "cadence": "Weekly",
                "artifact": "ch19_cash_forecast_13w_scenarios.csv",
                "escalation_trigger": "If buffer_trigger is True for any scenario in next 4 weeks.",
            },
            {
                "item": "Collections assumptions",
                "description": "Review AR collections behavior (aging, large invoices, disputes).",
                "owner_role": "AR lead",
                "cadence": "Weekly",
                "artifact": "AR aging + collections notes",
                "escalation_trigger": "If stressed scenario shows cash < buffer for 2+ consecutive weeks.",
            },
            {
                "item": "Payments discipline",
                "description": "Confirm AP payment plan and supplier term changes.",
                "owner_role": "AP lead",
                "cadence": "Weekly",
                "artifact": "AP aging + payment run",
                "escalation_trigger": "If supplier terms tighten or a key vendor changes terms.",
            },
            {
                "item": "Cash governance",
                "description": "Decide actions when triggers fire (delay discretionary spend, expedite collections, renegotiate terms).",
                "owner_role": "CFO / Owner",
                "cadence": "As-needed",
                "artifact": "ch19_memo.md",
                "escalation_trigger": "Projected ending cash < buffer_target (any scenario).",
            },
        ]
    )

    cash_governance_template_csv = outdir / "ch19_cash_governance_template.csv"
    governance.to_csv(cash_governance_template_csv, index=False)

    # -------------------------------
    # 4) Design JSON + memo
    # -------------------------------
    design = {
        "chapter": CHAPTER,
        "horizon_weeks": 13,
        "scenarios": scenarios,
        "data_sources": {
            "bank_statement": "bank_statement.csv",
            "ar_events": "ar_events.csv",
            "ap_events": "ap_events.csv",
            "payroll_events": "payroll_events.csv",
            "sales_tax_events": "sales_tax_events.csv",
            "debt_schedule": "debt_schedule.csv",
        },
        "direct_method": {
            "definition": "Cash receipts and cash payments, forecast at weekly granularity.",
            "note": "Use as a planning baseline; confirm large known events manually.",
        },
        "buffer_policy": {
            "buffer_target": float(buffer_target),
            "method": "p90 of negative weekly net cash flows (recent history)",
        },
        "stress_tests": {
            "delayed_collections": "Shift 20% of AR collections two weeks later.",
            "supplier_terms_tighten": "Increase key supplier cash outflows by 15%.",
        },
    }

    design_json = outdir / "ch19_design.json"
    design_json.write_text(json.dumps(design, indent=2, sort_keys=True), encoding="utf-8")

    # A short memo (CFO-style)
    memo_lines: list[str] = []
    memo_lines.append(f"# {CHAPTER} — 13-week cash forecast (direct method)\n")
    memo_lines.append("This forecast is a **planning baseline**. It is not a guarantee.")
    memo_lines.append("\n## Key points\n")
    memo_lines.append(f"- Starting cash (end of history): **{start_cash:,.0f}**")
    memo_lines.append(f"- Buffer target: **{buffer_target:,.0f}** (trigger when projected ending cash falls below this)")
    memo_lines.append("- Scenarios: Base, delayed collections, and tighter supplier terms")

    # Base scenario preview table (next 4 weeks)
    base_preview = (
        fc.loc[fc["scenario"] == "Base", ["week_start", "cash_in_total", "cash_out_total", "ending_cash", "buffer_trigger"]]
        .head(4)
        .copy()
    )
    memo_lines.append("\n## Base scenario: next 4 weeks\n")
    memo_lines.append(base_preview.to_markdown(index=False))

    memo_lines.append("\n## Guardrails\n")
    memo_lines.append(
        "- Treat timing assumptions as **editable** (collections delays, payment runs, tax remittances).\n"
        "- Do not over-interpret patterns: this is a short horizon meant for **cash governance**.\n"
        "- When triggers fire, document actions and owners (see governance template)."
    )

    memo_md = outdir / "ch19_memo.md"
    memo_md.write_text("\n".join(memo_lines) + "\n", encoding="utf-8")

    # -------------------------------
    # 5) Figures + manifest
    # -------------------------------
    manifest_rows: list[FigureManifestRow] = []

    def _add_row(fig_path: Path, spec: FigureSpec) -> None:
        manifest_rows.append(
            FigureManifestRow(
                filename=fig_path.name,
                chart_type=spec.chart_type,
                title=spec.title,
                x_label=spec.x_label,
                y_label=spec.y_label,
                data_source="NSO v1 synthetic outputs",
                guardrail_note=(
                    "Short-term cash forecasts depend on timing assumptions. "
                    "Treat outputs as planning baselines; confirm large known events."
                ),
            )
        )

    # Figure 1: history net cash flow (last 26 weeks)
    if not hist.empty:
        hist_tail = hist.tail(min(len(hist), 26)).copy()
        with style_context():
            fig = plot_time_series(
                hist_tail,
                x="week_start",
                series={"Net cash flow": "net_cash_flow"},
                title="Weekly net cash flow (recent history)",
                x_label="Week start",
                y_label="Net cash flow",
                show_zero_line=True,
            )
            spec = FigureSpec(
                chart_type="line",
                title="Weekly net cash flow (recent history)",
                x_label="Week start",
                y_label="Net cash flow",
                data_source="bank_statement.csv",
                notes="Direct method: receipts minus payments, aggregated weekly.",
            )
            fig_path = figures_dir / "ch19_fig_weekly_net_cash_flow_history.png"
            save_figure(fig, fig_path, spec=spec)
            _add_row(fig_path, spec)

    # Figure 2: forecast ending cash by scenario
    fc_wide = (
        fc.pivot_table(index="week_start", columns="scenario", values="ending_cash", aggfunc="mean", fill_value=0.0)
        .reset_index()
        .sort_values("week_start")
        .reset_index(drop=True)
    )

    series_map = {f"Ending cash ({c})": c for c in scenarios if c in fc_wide.columns}

    with style_context():
        fig = plot_time_series(
            fc_wide,
            x="week_start",
            series=series_map,
            title="13-week cash balance forecast by scenario",
            x_label="Week start",
            y_label="Ending cash",
        )
        spec = FigureSpec(
            chart_type="line",
            title="13-week cash balance forecast by scenario",
            x_label="Week start",
            y_label="Ending cash",
            data_source="bank_statement.csv + scenario adjustments",
            notes="Use Base for baseline planning; stresses show downside risk.",
        )
        fig_path = figures_dir / "ch19_fig_cash_balance_forecast_by_scenario.png"
        save_figure(fig, fig_path, spec=spec)
        _add_row(fig_path, spec)

    figures_manifest_csv = outdir / "ch19_figures_manifest.csv"
    pd.DataFrame([r.__dict__ for r in manifest_rows]).to_csv(figures_manifest_csv, index=False)

    return Outputs(
        cash_history_weekly_csv=cash_history_weekly_csv,
        cash_forecast_13w_scenarios_csv=cash_forecast_13w_scenarios_csv,
        cash_assumptions_csv=cash_assumptions_csv,
        cash_governance_template_csv=cash_governance_template_csv,
        design_json=design_json,
        memo_md=memo_md,
        figures_manifest_csv=figures_manifest_csv,
    )


def _build_cli() -> Any:
    p = base_parser(description=CHAPTER)
    p.add_argument("--datadir", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_cli()
    args = p.parse_args(argv)

    analyze_ch19(datadir=args.datadir, outdir=args.outdir, seed=args.seed or 123)
    print("Wrote Chapter 19 artifacts ->", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
