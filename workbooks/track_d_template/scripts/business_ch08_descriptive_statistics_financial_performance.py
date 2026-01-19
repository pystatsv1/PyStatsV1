# SPDX-License-Identifier: MIT
# business_ch08_descriptive_statistics_financial_performance.py
"""Track D Business Chapter 8: Descriptive statistics for financial performance.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* gl_kpi_monthly.csv
* ar_monthly_metrics.csv
* ar_payment_slices.csv
* ar_days_stats.csv
* ch08_summary.json

This chapter takes the NSO v1 synthetic bookkeeping dataset and produces
analysis-ready *descriptive* tables that accountants and analysts use to
understand performance variability.

Outputs
-------
- gl_kpi_monthly.csv
    Monthly income-statement KPIs + ratios + small rolling volatility signals.
- ar_monthly_metrics.csv
    Accounts Receivable (A/R) roll-forward metrics such as collections rate and
    an approximate Days Sales Outstanding (DSO).
- ar_payment_slices.csv
    A small “payment lag” distribution built by applying cash collections to
    invoices using a FIFO rule (good for mean vs median demonstrations).
- ar_days_stats.csv
    Overall + per-customer summary stats (mean/median/quantiles/std) for the
    payment-lag distribution.
- ch08_summary.json
    Run report: row counts, checks, and a short data dictionary.

Design goals
------------
- Deterministic (seeded)
- Small, readable CSVs
- Chapter runs standalone from the raw NSO v1 folder"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ._business_etl import build_gl_tidy_dataset
from ._cli import base_parser


@dataclass(frozen=True)
class Ch08Outputs:
    gl_kpi_monthly: pd.DataFrame
    ar_monthly_metrics: pd.DataFrame
    ar_payment_slices: pd.DataFrame
    ar_days_stats: pd.DataFrame
    summary: dict[str, Any]


def _read_csv_required(datadir: Path, filename: str, *, fallbacks: list[str] | None = None) -> pd.DataFrame:
    """Read a required CSV, optionally trying fallback filenames.

    This keeps chapters robust when the simulator/export names evolve.
    """
    candidates = [filename] + (fallbacks or [])
    for name in candidates:
        path = datadir / name
        if path.exists():
            return pd.read_csv(path)
    # If none found, raise using the primary expected name (so error is clear)
    raise FileNotFoundError(datadir / filename)


def _pivot_statement(df: pd.DataFrame) -> pd.DataFrame:
    """Return a wide statement frame: index month, columns = line."""
    out = df.pivot_table(index="month", columns="line", values="amount", aggfunc="sum")
    out = out.sort_index()
    out.columns = [str(c) for c in out.columns]
    return out.reset_index()


def _col(df: pd.DataFrame, name: str, default: float = 0.0) -> pd.Series:
    """Return df[name] as a float Series, or a default-valued Series if missing."""
    if name in df.columns:
        return df[name].astype(float)
    return pd.Series([float(default)] * len(df), index=df.index, dtype=float)


def _days_in_month(month: str) -> int:
    # month like "2025-01"
    p = pd.Period(month, freq="M")
    return int(p.days_in_month)


def _safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    return numer.where(denom.abs() > 1e-12, np.nan) / denom.where(denom.abs() > 1e-12, np.nan)


def _describe_numeric(values: np.ndarray) -> dict[str, float]:
    if values.size == 0:
        return {
            "n": 0.0,
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "min": np.nan,
            "p25": np.nan,
            "p75": np.nan,
            "p90": np.nan,
            "max": np.nan,
        }
    v = values.astype(float)
    return {
        "n": float(v.size),
        "mean": float(np.nanmean(v)),
        "median": float(np.nanmedian(v)),
        "std": float(np.nanstd(v, ddof=1)) if v.size > 1 else 0.0,
        "min": float(np.nanmin(v)),
        "p25": float(np.nanpercentile(v, 25)),
        "p75": float(np.nanpercentile(v, 75)),
        "p90": float(np.nanpercentile(v, 90)),
        "max": float(np.nanmax(v)),
    }


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    """Weighted median of values using non-negative weights."""
    if values.size == 0:
        return float("nan")
    w = np.asarray(weights, dtype=float)
    v = np.asarray(values, dtype=float)
    if np.any(w < 0):
        raise ValueError("weights must be non-negative")
    if np.all(w == 0):
        return float(np.nanmedian(v))
    order = np.argsort(v)
    v_sorted = v[order]
    w_sorted = w[order]
    cum = np.cumsum(w_sorted)
    cutoff = 0.5 * float(np.sum(w_sorted))
    idx = int(np.searchsorted(cum, cutoff, side="left"))
    return float(v_sorted[min(idx, v_sorted.size - 1)])


def _ar_payment_slices(ar_events: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build a payment-lag distribution by applying collections to invoices.

    We treat invoices as positive A/R increases and collections as positive cash
    received. Collections are applied FIFO to the oldest open invoices.

    Returns (slices_df, diagnostics).
    """
    required = {"date", "customer", "event_type", "amount"}
    missing = required - set(map(str, ar_events.columns))
    if missing:
        raise ValueError(f"ar_events is missing required columns: {sorted(missing)}")

    df = ar_events.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "customer", "event_type", "amount"])
    df = df.sort_values(["customer", "date", "txn_id"], kind="mergesort")

    rows: list[dict[str, Any]] = []
    unapplied_total = 0.0
    open_invoices_end: list[dict[str, Any]] = []

    for customer, sub in df.groupby("customer", sort=False):
        open_q: deque[dict[str, Any]] = deque()
        for _, r in sub.iterrows():
            et = str(r["event_type"]).lower().strip()
            amt = float(r["amount"])
            if amt <= 0:
                continue

            if et == "invoice":
                open_q.append(
                    {
                        "invoice_id": str(r.get("invoice_id", "")),
                        "invoice_date": pd.Timestamp(r["date"]).normalize(),
                        "remaining": amt,
                    }
                )
                continue

            if et != "collection":
                continue

            pay_date = pd.Timestamp(r["date"]).normalize()
            remaining = amt

            while remaining > 1e-9 and len(open_q) > 0:
                inv = open_q[0]
                applied = min(float(inv["remaining"]), remaining)
                days = int((pay_date - pd.Timestamp(inv["invoice_date"])).days)
                rows.append(
                    {
                        "customer": customer,
                        "invoice_id": inv["invoice_id"],
                        "invoice_date": pd.Timestamp(inv["invoice_date"]).strftime("%Y-%m-%d"),
                        "payment_date": pay_date.strftime("%Y-%m-%d"),
                        "month_paid": pay_date.strftime("%Y-%m"),
                        "amount_applied": float(applied),
                        "days_outstanding": float(days),
                    }
                )
                inv["remaining"] = float(inv["remaining"]) - float(applied)
                remaining -= float(applied)
                if inv["remaining"] <= 1e-9:
                    open_q.popleft()

            if remaining > 1e-9:
                unapplied_total += float(remaining)

        # keep open invoices at the end (diagnostic only)
        if len(open_q) > 0:
            asof = sub["date"].max().normalize()
            for inv in list(open_q):
                open_invoices_end.append(
                    {
                        "customer": customer,
                        "invoice_id": inv["invoice_id"],
                        "invoice_date": pd.Timestamp(inv["invoice_date"]).strftime("%Y-%m-%d"),
                        "remaining_amount": float(inv["remaining"]),
                        "age_days_asof_end": float((asof - pd.Timestamp(inv["invoice_date"])).days),
                    }
                )

    slices = pd.DataFrame(rows)
    if slices.empty:
        slices = pd.DataFrame(
            columns=[
                "customer",
                "invoice_id",
                "invoice_date",
                "payment_date",
                "month_paid",
                "amount_applied",
                "days_outstanding",
            ]
        )

    diagnostics = {
        "unapplied_collections_total": float(unapplied_total),
        "open_invoices_end": open_invoices_end,
    }
    return slices, diagnostics


def _ar_days_stats(slices: pd.DataFrame) -> pd.DataFrame:
    """Summarize days outstanding overall + by customer."""
    if slices.empty:
        return pd.DataFrame(
            columns=[
                "customer",
                "n",
                "mean_days",
                "median_days",
                "weighted_mean_days",
                "weighted_median_days",
                "std_days",
                "p25_days",
                "p75_days",
                "p90_days",
                "min_days",
                "max_days",
                "total_paid",
            ]
        )

    def _one(g: pd.DataFrame) -> dict[str, Any]:
        days = g["days_outstanding"].to_numpy(dtype=float)
        amt = g["amount_applied"].to_numpy(dtype=float)
        desc = _describe_numeric(days)
        weighted_mean = float(np.sum(days * amt) / np.sum(amt)) if np.sum(amt) > 1e-12 else float(np.nan)
        weighted_med = _weighted_median(days, amt)
        return {
            "n": int(desc["n"]),
            "mean_days": desc["mean"],
            "median_days": desc["median"],
            "weighted_mean_days": weighted_mean,
            "weighted_median_days": weighted_med,
            "std_days": desc["std"],
            "p25_days": desc["p25"],
            "p75_days": desc["p75"],
            "p90_days": desc["p90"],
            "min_days": desc["min"],
            "max_days": desc["max"],
            "total_paid": float(np.sum(amt)),
        }

    out_rows: list[dict[str, Any]] = []
    for customer, g in slices.groupby("customer", sort=False):
        row = {"customer": str(customer)}
        row.update(_one(g))
        out_rows.append(row)

    overall = {"customer": "ALL"}
    overall.update(_one(slices))
    out_rows.append(overall)

    return pd.DataFrame(out_rows)


def analyze_ch08(datadir: Path, outdir: Path | None = None, seed: int = 123) -> Ch08Outputs:
    """Run Chapter 8 analysis and return outputs as dataframes."""
    # Build analysis-ready GL (Chapter 7 logic) directly from raw exports
    gl = _read_csv_required(datadir, "gl_journal.csv", fallbacks=["gl.csv", "general_ledger.csv"])
    coa = _read_csv_required(datadir, "chart_of_accounts.csv", fallbacks=["coa.csv"])
    gl_tidy = build_gl_tidy_dataset(gl, coa)

    # Statements are already monthly and are a stable “accounting truth” for KPIs
    is_df = _read_csv_required(datadir, "statements_is_monthly.csv")
    bs_df = _read_csv_required(datadir, "statements_bs_monthly.csv")
    is_w = _pivot_statement(is_df)
    bs_w = _pivot_statement(bs_df)

    # Ensure month alignment
    months = sorted(set(is_w["month"]).intersection(set(bs_w["month"])))
    is_w = is_w.loc[is_w["month"].isin(months)].copy()
    bs_w = bs_w.loc[bs_w["month"].isin(months)].copy()
    is_w = is_w.sort_values("month").reset_index(drop=True)
    bs_w = bs_w.sort_values("month").reset_index(drop=True)

    # KPIs
    roll_window = 3  # small default window for “volatility” signals

    kpi = pd.DataFrame({"month": is_w["month"].astype(str)})
    kpi["revenue"] = _col(is_w, "Sales Revenue", 0.0)
    kpi["cogs"] = _col(is_w, "Cost of Goods Sold", 0.0)

    if "Gross Profit" in is_w.columns:
        kpi["gross_profit"] = is_w["Gross Profit"].astype(float)
    else:
        kpi["gross_profit"] = (kpi["revenue"] - kpi["cogs"]).astype(float)

    kpi["operating_expenses"] = _col(is_w, "Total Operating Expenses", 0.0)
    kpi["net_income"] = _col(is_w, "Net Income", 0.0)

    kpi["gross_margin_pct"] = _safe_div(kpi["gross_profit"], kpi["revenue"]).replace([np.inf, -np.inf], np.nan)
    kpi["net_margin_pct"] = _safe_div(kpi["net_income"], kpi["revenue"]).replace([np.inf, -np.inf], np.nan)
    kpi["revenue_growth_pct"] = kpi["revenue"].pct_change().replace([np.inf, -np.inf], np.nan)

    for col in ["gross_margin_pct", "net_margin_pct", "revenue_growth_pct"]:
        kpi[f"{col}_roll_mean_w{roll_window}"] = kpi[col].rolling(window=roll_window, min_periods=1).mean()
        kpi[f"{col}_roll_std_w{roll_window}"] = kpi[col].rolling(window=roll_window, min_periods=2).std(ddof=1)
        kpi[f"{col}_zscore"] = _safe_div(
            kpi[col] - kpi[f"{col}_roll_mean_w{roll_window}"],
            kpi[f"{col}_roll_std_w{roll_window}"],
        )

    # Add a few balance-sheet anchors (useful for “ratio thinking”)
    kpi["cash_end"] = bs_w.get("Cash", np.nan).astype(float)
    kpi["ar_end"] = bs_w.get("Accounts Receivable", np.nan).astype(float)
    kpi["inventory_end"] = bs_w.get("Inventory", np.nan).astype(float)
    kpi["ap_end"] = bs_w.get("Accounts Payable", np.nan).astype(float)

    # A/R monthly metrics from tidy GL (credit sales, collections) + BS balances
    ar_lines = gl_tidy.loc[gl_tidy["account_id"].astype(str) == "1100"].copy()
    ar_lines["month"] = ar_lines["date"].astype(str).str.slice(0, 7)
    ar_lines["signed"] = ar_lines["debit"].astype(float) - ar_lines["credit"].astype(float)

    ar_month = (
        ar_lines.groupby("month", observed=True)
        .agg(
            credit_sales=("signed", lambda s: float(np.sum(np.clip(s.to_numpy(dtype=float), 0, None)))),
            collections=("signed", lambda s: float(np.sum(np.clip(-s.to_numpy(dtype=float), 0, None)))),
        )
        .reset_index()
    )
    ar_month = ar_month.loc[ar_month["month"].isin(months)].copy()
    ar_month = ar_month.sort_values("month").reset_index(drop=True)
    ar_month["ar_end"] = kpi["ar_end"].astype(float)
    ar_month["ar_begin"] = ar_month["ar_end"].shift(1)
    if not ar_month.empty:
        ar_month.loc[0, "ar_begin"] = ar_month.loc[0, "ar_end"]
    ar_month["avg_ar"] = 0.5 * (ar_month["ar_begin"] + ar_month["ar_end"])
    ar_month["days_in_month"] = ar_month["month"].astype(str).apply(_days_in_month).astype(int)
    ar_month["ar_turnover"] = _safe_div(ar_month["credit_sales"], ar_month["avg_ar"]).replace([np.inf, -np.inf], np.nan)
    ar_month["dso"] = _safe_div(ar_month["avg_ar"], ar_month["credit_sales"]).replace([np.inf, -np.inf], np.nan) * ar_month[
        "days_in_month"
    ]
    ar_month["collections_rate"] = _safe_div(ar_month["collections"], ar_month["credit_sales"]).replace(
        [np.inf, -np.inf], np.nan
    )

    # A/R “days outstanding” distribution (payment slices)
    ar_events = _read_csv_required(datadir, "ar_events.csv") if (datadir / "ar_events.csv").exists() else pd.DataFrame()
    slices, ar_diag = _ar_payment_slices(ar_events) if not ar_events.empty else (
        pd.DataFrame(
            columns=[
                "customer",
                "invoice_id",
                "invoice_date",
                "payment_date",
                "month_paid",
                "amount_applied",
                "days_outstanding",
            ]
        ),
        {"unapplied_collections_total": 0.0, "open_invoices_end": []},
    )

    ar_days_stats = _ar_days_stats(slices)

    # Summary report (minimal, consistent with earlier chapters)
    checks = {
        "months": months,
        "n_months": int(len(months)),
        "kpi_rows": int(len(kpi)),
        "ar_monthly_rows": int(len(ar_month)),
        "ar_payment_slices_rows": int(len(slices)),
        "gross_margin_pct_in_range": bool(
            kpi["gross_margin_pct"].dropna().between(-1.0, 1.0).all() if not kpi.empty else True
        ),
        "dso_nonnegative": bool(ar_month["dso"].dropna().ge(0.0).all() if not ar_month.empty else True),
    }

    data_dictionary = {
        "gl_kpi_monthly.csv": {
            "grain": "one row per month",
            "notes": "Income statement KPIs + ratios + rolling mean/std + z-scores.",
        },
        "ar_monthly_metrics.csv": {
            "grain": "one row per month",
            "notes": "Credit sales and collections inferred from AR account activity; includes DSO approximation.",
        },
        "ar_payment_slices.csv": {
            "grain": "one row per payment slice",
            "notes": "FIFO allocation of collections to invoices; used to illustrate skew (mean vs median).",
        },
        "ar_days_stats.csv": {
            "grain": "one row per customer plus ALL",
            "notes": "Summary stats for days outstanding (unweighted + amount-weighted).",
        },
        "ch08_summary.json": {
            "grain": "one JSON document",
            "notes": "Row counts, checks, and A/R diagnostics.",
        },
    }

    summary: dict[str, Any] = {
        "chapter": "business_ch08_descriptive_statistics_financial_performance",
        "seed": int(seed),
        "checks": checks,
        "ar_diagnostics": {
            "unapplied_collections_total": float(ar_diag.get("unapplied_collections_total", 0.0)),
            "open_invoices_end_count": int(len(ar_diag.get("open_invoices_end", []))),
        },
        "data_dictionary": data_dictionary,
    }

    outputs = Ch08Outputs(
        gl_kpi_monthly=kpi,
        ar_monthly_metrics=ar_month,
        ar_payment_slices=slices,
        ar_days_stats=ar_days_stats,
        summary=summary,
    )

    # If outdir is provided, write artifacts (keeps CLI + tests simple)
    if outdir is not None:
        write_ch08(outputs, Path(outdir))

    return outputs


def write_ch08(outputs: Ch08Outputs, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs.gl_kpi_monthly.to_csv(outdir / "gl_kpi_monthly.csv", index=False)
    outputs.ar_monthly_metrics.to_csv(outdir / "ar_monthly_metrics.csv", index=False)
    outputs.ar_payment_slices.to_csv(outdir / "ar_payment_slices.csv", index=False)
    outputs.ar_days_stats.to_csv(outdir / "ar_days_stats.csv", index=False)
    (outdir / "ch08_summary.json").write_text(json.dumps(outputs.summary, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = base_parser("Business Ch08: descriptive stats for financial performance")
    p.add_argument("--datadir", type=str, required=True, help="Path to NSO v1 dataset folder")
    args = p.parse_args(argv)

    seed = int(args.seed) if args.seed is not None else 123
    analyze_ch08(Path(args.datadir), outdir=Path(args.outdir), seed=seed)
    print(f"Wrote Chapter 8 artifacts -> {Path(args.outdir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
