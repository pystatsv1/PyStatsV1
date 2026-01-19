# SPDX-License-Identifier: MIT
# business_ch10_probability_risk.py
"""Track D — Business Statistics & Forecasting for Accountants.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch10_figures_manifest.csv
* ch10_risk_memo.md
* ch10_risk_summary.json

Chapter 10: Probability and Risk in Business Terms

This chapter translates abstract probability into concrete operational risk.

Outputs are designed to be:
- deterministic (seeded)
- audit-friendly (explicit assumptions + defensible calculations)
- matplotlib-only (no seaborn)

We focus on two common small-business risks:
1) Cash shortfall risk -> size an emergency fund so cash stays >= 0 with ~95% confidence.
2) Bad debt risk (A/R) -> estimate expected loss and a p90 "worst-case" loss.

The goal is not perfect forecasting; it is honest, explainable risk communication."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts._cli import apply_seed, base_parser
from scripts._reporting_style import (
    FigureManifestRow,
    FigureSpec,
    plot_ecdf,
    plot_histogram_with_markers,
    save_figure,
    style_context,
)
from scripts.business_ch08_descriptive_statistics_financial_performance import analyze_ch08


# --- Guardrails / defaults (explicit + testable) ---

DEFAULT_HORIZON_MONTHS = 12
DEFAULT_N_SIMS = 5000
DEFAULT_CONFIDENCE = 0.95

# A/R late threshold used as a *proxy* for default risk.
DEFAULT_SEVERE_LATE_DAYS = 90

# Loss-given-default (LGD) assumption used in this toy model.
DEFAULT_LGD = 1.0

# Rounding for "no false precision" communication.
_MONEY_ROUND_TO = 100.0


@dataclass(frozen=True)
class Ch10Outputs:
    manifest_path: Path
    memo_path: Path
    summary_path: Path
    figures_dir: Path
    figure_paths: list[Path]


def _read_csv_required(datadir: Path, fname: str) -> pd.DataFrame:
    path = datadir / fname
    if not path.exists():
        raise FileNotFoundError(f"Missing required dataset file: {path}")
    return pd.read_csv(path)


def _latest_bs_value(bs: pd.DataFrame, line_name: str) -> float:
    """Return latest month amount for a given balance sheet line."""

    if bs.empty:
        return float("nan")

    if {"month", "line", "amount"}.issubset(set(bs.columns)):
        df = bs.loc[bs["line"].astype(str) == str(line_name)].copy()
        if df.empty:
            return float("nan")
        df["month"] = df["month"].astype(str)
        df = df.sort_values("month", kind="mergesort")
        return float(df.iloc[-1]["amount"])

    # Fallback: try a common alternative schema.
    if "line" in bs.columns and "amount" in bs.columns:
        df = bs.loc[bs["line"].astype(str) == str(line_name)].copy()
        if df.empty:
            return float("nan")
        return float(df["amount"].iloc[-1])

    return float("nan")


def _monthly_net_cash_changes(bank: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bank statement transactions into monthly net cash change."""

    if bank.empty:
        return pd.DataFrame(columns=["month", "net_cash_change"])

    if not {"month", "amount"}.issubset(set(bank.columns)):
        raise ValueError("bank_statement.csv must contain columns: month, amount")

    df = bank.copy()
    df["month"] = df["month"].astype(str)
    df["amount"] = df["amount"].astype(float)

    out = (
        df.groupby("month", observed=True)["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "net_cash_change"})
        .sort_values("month", kind="mergesort")
        .reset_index(drop=True)
    )
    return out


def _bootstrap_cash_buffer(
    net_changes: np.ndarray,
    current_cash: float,
    horizon_months: int,
    n_sims: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Bootstrap resampling model for cash shortfall risk.

    We resample historical monthly net cash changes with replacement.

    Returns
    -------
    Dict with:
    - buffer_needed: array of required buffer per simulation
    - p_shortfall: prob(cash dips below 0 at least once) without extra buffer
    - buffer_p95: 95th percentile buffer
    """

    if net_changes.size == 0 or not np.isfinite(float(current_cash)):
        return {
            "buffer_needed": np.array([], dtype=float),
            "p_shortfall": float("nan"),
            "buffer_p95": float("nan"),
            "buffer_mean": float("nan"),
        }

    draws = rng.choice(net_changes.astype(float), size=(int(n_sims), int(horizon_months)), replace=True)
    balances = float(current_cash) + np.cumsum(draws, axis=1)
    min_bal = np.min(balances, axis=1)

    buffer_needed = np.maximum(0.0, -min_bal)
    p_shortfall = float(np.mean(min_bal < 0.0))

    buffer_p95 = float(np.nanpercentile(buffer_needed, 95))
    buffer_mean = float(np.nanmean(buffer_needed))

    return {
        "buffer_needed": buffer_needed,
        "p_shortfall": p_shortfall,
        "buffer_p95": buffer_p95,
        "buffer_mean": buffer_mean,
    }


def _severe_late_rates_from_slices(slices: pd.DataFrame, severe_late_days: int) -> np.ndarray:
    """Compute monthly severe-late share as a proxy for bad-debt risk.

    Rate per month = (sum(amount_applied where days_outstanding >= threshold)) / (sum(amount_applied)).

    Note: This is not a true default model; it's a pedagogical proxy.
    """

    if slices.empty:
        return np.array([], dtype=float)

    required = {"month_paid", "days_outstanding", "amount_applied"}
    if not required.issubset(set(slices.columns)):
        return np.array([], dtype=float)

    df = slices.copy()
    df["month_paid"] = df["month_paid"].astype(str)
    df["days_outstanding"] = df["days_outstanding"].astype(float)
    df["amount_applied"] = df["amount_applied"].astype(float)

    df["is_severe_late"] = df["days_outstanding"] >= float(severe_late_days)

    # Compute severe-late share per month without groupby.apply (avoids pandas FutureWarning).
    monthly = (
        df.groupby(["month_paid", "is_severe_late"], observed=True)["amount_applied"]
        .sum()
        .unstack(fill_value=0.0)
    )

    severe = monthly.get(True, pd.Series(0.0, index=monthly.index))
    total = monthly.sum(axis=1).replace(0.0, np.nan)

    grouped = severe / total

    rates = grouped.to_numpy(dtype=float)
    rates = rates[np.isfinite(rates)]
    return rates


def _fmt_money(x: float, round_to: float = _MONEY_ROUND_TO) -> str:
    """Format money without false precision (round first)."""

    if not np.isfinite(float(x)):
        return "n/a"

    xr = float(np.round(float(x) / float(round_to)) * float(round_to))
    sign = "-" if xr < 0 else ""
    xr = abs(xr)

    if xr >= 1_000_000:
        return f"{sign}${xr/1_000_000:.1f}M"
    if xr >= 1_000:
        return f"{sign}${xr/1_000:.1f}k"
    return f"{sign}${xr:.0f}"


def _prob_to_frequency(p: float) -> str:
    """Translate probability into an intuitive "1 out of every N" statement."""

    if not np.isfinite(float(p)):
        return "n/a"
    p = float(p)
    if p <= 0:
        return "rare/none observed"
    if p >= 1:
        return "every month"

    n = int(round(1.0 / p))
    n = max(1, n)
    return f"about 1 out of every {n} months"


def _make_risk_memo(
    *,
    latest_month: str,
    current_cash: float,
    current_ar: float,
    cash_buffer_p95: float,
    p_shortfall: float,
    expected_loss: float,
    worst_case_p90_loss: float,
    severe_late_days: int,
    lgd: float,
    horizon_months: int,
) -> str:
    """Return a short, deterministic markdown memo (<= 10 bullets)."""

    bullets: list[str] = []

    bullets.append(
        f"Cash risk (as of {latest_month}): current cash is {_fmt_money(current_cash)}. "
        f"Using a bootstrap of historical monthly net cash changes, the probability of cash dipping below $0 at least once in the next {horizon_months} months is {p_shortfall:.1%} "
        f"({_prob_to_frequency(p_shortfall)})."
    )

    bullets.append(
        f"Recommended emergency fund (95% confidence): {_fmt_money(cash_buffer_p95)}. "
        "Interpretation: adding this buffer to the current cash balance keeps simulated paths >= $0 in ~95% of scenarios under the model assumptions."
    )

    bullets.append(
        f"Bad debt risk (A/R): current A/R is {_fmt_money(current_ar)}. "
        f"Using severe-late payments (≥ {severe_late_days} days) as a proxy for default risk and LGD={lgd:.0%}, the expected loss is {_fmt_money(expected_loss)}."
    )

    bullets.append(
        f"Bad debt worst case (p90): {_fmt_money(worst_case_p90_loss)}. "
        "Interpretation: in 1 out of 10 months like the high-risk tail of recent history, losses could be this large (or larger)."
    )

    bullets.append(
        "Assumptions (explicit): (1) future cash-change months are resampled from recent history (no structural change), "
        "(2) months are treated as independent (no seasonality model), "
        "(3) severe-late share is a proxy for default (not a true write-off model), "
        "(4) numbers are rounded to avoid false precision."
    )

    bullets.append(
        "Unknown unknowns to monitor: customer concentration risk, one-time cash shocks (taxes, capex, fraud), "
        "credit policy changes, supply disruptions, and accounting system/process changes that break comparability."
    )

    # Keep <= 10 bullets (contract guardrail)
    bullets = bullets[:10]

    return "\n".join([f"- {b}" for b in bullets]) + "\n"


def analyze_ch10(
    *,
    datadir: Path,
    outdir: Path | None,
    seed: int = 123,
    horizon_months: int = DEFAULT_HORIZON_MONTHS,
    n_sims: int = DEFAULT_N_SIMS,
    severe_late_days: int = DEFAULT_SEVERE_LATE_DAYS,
    lgd: float = DEFAULT_LGD,
) -> Ch10Outputs:
    """Run Chapter 10 analysis and write deterministic artifacts."""

    apply_seed(seed)

    if outdir is None:
        outdir = Path("outputs/track_d")

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = outdir / "ch10_figures_manifest.csv"
    memo_path = outdir / "ch10_risk_memo.md"
    summary_path = outdir / "ch10_risk_summary.json"

    # --- Inputs ---
    bs = _read_csv_required(datadir, "statements_bs_monthly.csv")
    bank = _read_csv_required(datadir, "bank_statement.csv")

    # Latest month for labels
    latest_month = str(bs["month"].astype(str).max()) if "month" in bs.columns and not bs.empty else "(unknown)"

    current_cash = _latest_bs_value(bs, "Cash")
    current_ar = _latest_bs_value(bs, "Accounts Receivable")

    # Monthly net cash change distribution
    bank_m = _monthly_net_cash_changes(bank)
    net_changes = bank_m["net_cash_change"].astype(float).to_numpy() if not bank_m.empty else np.array([], dtype=float)

    rng = np.random.default_rng(int(seed) + 10_000)
    cash_sim = _bootstrap_cash_buffer(
        net_changes=net_changes,
        current_cash=float(current_cash),
        horizon_months=int(horizon_months),
        n_sims=int(n_sims),
        rng=rng,
    )

    buffer_needed = cash_sim["buffer_needed"]
    p_shortfall = float(cash_sim["p_shortfall"])
    buffer_p95 = float(cash_sim["buffer_p95"])
    buffer_mean = float(cash_sim["buffer_mean"])

    # Bad debt proxy from Chapter 8 A/R payment lag slices
    ch08 = analyze_ch08(datadir=datadir, outdir=None, seed=seed)
    rates = _severe_late_rates_from_slices(ch08.ar_payment_slices, severe_late_days=int(severe_late_days))

    expected_rate = float(np.nanmean(rates)) if rates.size else float("nan")
    p90_rate = float(np.nanpercentile(rates, 90)) if rates.size else float("nan")

    expected_loss = float(current_ar) * float(lgd) * expected_rate if np.isfinite(current_ar) else float("nan")
    worst_case_p90_loss = float(current_ar) * float(lgd) * p90_rate if np.isfinite(current_ar) else float("nan")

    # --- Figures (style contract compliant) ---
    manifest: list[FigureManifestRow] = []
    figure_paths: list[Path] = []

    # 1) Histogram of monthly net cash changes
    if net_changes.size:
        markers = {
            "mean": float(np.mean(net_changes)),
            "median": float(np.median(net_changes)),
            "p10": float(np.percentile(net_changes, 10)),
            "p90": float(np.percentile(net_changes, 90)),
        }
        with style_context():
            fig = plot_histogram_with_markers(
                values=net_changes,
                title="Monthly net cash change — histogram",
                x_label="Net cash change (currency units)",
                y_label="Count",
                markers=markers,
            )
            path = figures_dir / "ch10_cash_flow_hist.png"
            save_figure(fig, path, FigureSpec(chart_type="histogram", title="Monthly net cash change — histogram"))
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="histogram",
                title="Monthly net cash change — histogram",
                x_label="Net cash change (currency units)",
                y_label="Count",
                guardrail_note="Histogram uses real units; include quantile markers to reveal tail risk.",
                data_source="bank_statement.csv (aggregated by month)",
            )
        )
        figure_paths.append(path)

    # 2) ECDF of buffer needed
    if buffer_needed.size:
        markers = {"p95": float(buffer_p95), "mean": float(buffer_mean)}
        with style_context():
            fig = plot_ecdf(
                values=buffer_needed,
                title=f"Emergency fund needed to keep cash ≥ 0 (horizon={horizon_months} months)",
                x_label="Buffer needed (currency units)",
                y_label="Cumulative proportion",
                markers=markers,
            )
            path = figures_dir / "ch10_cash_buffer_ecdf.png"
            save_figure(fig, path, FigureSpec(chart_type="ecdf", title="Emergency fund buffer ECDF"))
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="ecdf",
                title=f"Emergency fund needed (horizon={horizon_months} months)",
                x_label="Buffer needed (currency units)",
                y_label="Cumulative proportion",
                guardrail_note="ECDF communicates uncertainty; highlight p95 to avoid false precision.",
                data_source="bank_statement.csv (bootstrap resample of monthly net changes)",
            )
        )
        figure_paths.append(path)

    # 3) ECDF of bad-debt loss proxy (loss = AR * rate * LGD)
    if rates.size and np.isfinite(float(current_ar)):
        losses = float(current_ar) * float(lgd) * rates
        markers = {"expected": float(expected_loss), "p90": float(worst_case_p90_loss)}
        with style_context():
            fig = plot_ecdf(
                values=losses,
                title=f"Bad debt loss proxy (severe-late ≥ {severe_late_days} days)",
                x_label="Loss (currency units)",
                y_label="Cumulative proportion",
                markers=markers,
            )
            path = figures_dir / "ch10_bad_debt_loss_ecdf.png"
            save_figure(fig, path, FigureSpec(chart_type="ecdf", title="Bad debt loss proxy ECDF"))
        manifest.append(
            FigureManifestRow(
                filename=path.name,
                chart_type="ecdf",
                title=f"Bad debt loss proxy (severe-late ≥ {severe_late_days} days)",
                x_label="Loss (currency units)",
                y_label="Cumulative proportion",
                guardrail_note="Proxy model: severe-late share is not equal to true default; present as risk range.",
                data_source="ar_payment_slices.csv (via Ch08)",
            )
        )
        figure_paths.append(path)

    # --- Memo + summary ---
    memo = _make_risk_memo(
        latest_month=latest_month,
        current_cash=float(current_cash),
        current_ar=float(current_ar),
        cash_buffer_p95=float(buffer_p95),
        p_shortfall=float(p_shortfall),
        expected_loss=float(expected_loss),
        worst_case_p90_loss=float(worst_case_p90_loss),
        severe_late_days=int(severe_late_days),
        lgd=float(lgd),
        horizon_months=int(horizon_months),
    )
    memo_path.write_text(memo, encoding="utf-8")

    pd.DataFrame([m.__dict__ for m in manifest]).to_csv(manifest_path, index=False)

    summary: dict[str, Any] = {
        "chapter": "business_ch10_probability_risk",
        "seed": int(seed),
        "inputs": {
            "datadir": str(datadir),
            "files": ["statements_bs_monthly.csv", "bank_statement.csv", "ar_events.csv (via Ch08)"] ,
        },
        "assumptions": {
            "horizon_months": int(horizon_months),
            "n_sims": int(n_sims),
            "cash_model": "bootstrap monthly net cash change (bank statement aggregated by month)",
            "bad_debt_proxy": f"severe-late share of collections (>= {int(severe_late_days)} days)",
            "lgd": float(lgd),
            "rounding": float(_MONEY_ROUND_TO),
        },
        "cash_buffer": {
            "confidence": float(DEFAULT_CONFIDENCE),
                               "horizon_months": int(horizon_months),
                               "current_cash": float(current_cash),
                               "p_shortfall": float(p_shortfall),
                               "buffer_p95": float(buffer_p95),
                               "buffer_mean": float(buffer_mean),
                               "n_months_history": int(net_changes.size),
                     },
        "cash": {
                               "latest_month": latest_month,
                               "current_cash": float(current_cash),
                               "p_shortfall": float(p_shortfall),
                               "recommended_buffer_p95": float(buffer_p95),
                               "buffer_mean": float(buffer_mean),
                               "n_months_history": int(net_changes.size),
                     },

        "bad_debt": {
            "current_ar": float(current_ar),
            "expected_rate": float(expected_rate),
            "p90_rate": float(p90_rate),
            "expected_loss": float(expected_loss),
            # Preferred key name (matches tests / public schema)
            "worst_case_loss_p90": float(worst_case_p90_loss),
            # Back-compat key (safe to keep for now)
            "worst_case_p90_loss": float(worst_case_p90_loss),
            "n_months_rates": int(rates.size),
        },
        "paths": {
            "manifest": str(manifest_path),
            "memo": str(memo_path),
            "summary": str(summary_path),
            "figures_dir": str(figures_dir),
        },
        "figures": [p.name for p in figure_paths],
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return Ch10Outputs(
        manifest_path=manifest_path,
        memo_path=memo_path,
        summary_path=summary_path,
        figures_dir=figures_dir,
        figure_paths=figure_paths,
    )


def main(argv: list[str] | None = None) -> int:
    p = base_parser("Business Ch10: probability and risk")
    p.add_argument("--datadir", type=Path, required=True, help="Path to NSO v1 dataset folder")
    p.add_argument("--horizon-months", type=int, default=DEFAULT_HORIZON_MONTHS)
    p.add_argument("--n-sims", type=int, default=DEFAULT_N_SIMS)
    p.add_argument("--severe-late-days", type=int, default=DEFAULT_SEVERE_LATE_DAYS)
    p.add_argument("--lgd", type=float, default=DEFAULT_LGD)
    args = p.parse_args(argv)

    analyze_ch10(
        datadir=Path(args.datadir),
        outdir=Path(args.outdir),
        seed=int(args.seed) if args.seed is not None else 123,
        horizon_months=int(args.horizon_months),
        n_sims=int(args.n_sims),
        severe_late_days=int(args.severe_late_days),
        lgd=float(args.lgd),
    )

    print(f"Wrote Chapter 10 artifacts -> {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
