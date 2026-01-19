# SPDX-License-Identifier: MIT
"""Track D — Business Statistics for Accountants.

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch12_experiment_design.json
* ch12_hypothesis_testing_summary.json
* ch12_experiment_memo.md
* ch12_figures_manifest.csv

Chapter 12: Hypothesis Testing for Decisions (Practical, Not Math-Heavy)

This chapter reframes hypothesis testing as *business experimentation*.

NSO v1 doesn't contain explicit "region" or "promotion" labels, so we generate two
*deterministic teaching cases* from NSO v1 input data:

1) Promotion test (two groups):
   - Build two "regions" by deterministically assigning customers to treatment/control.
   - Choose a promo month with the most AR invoices.
   - Apply a small, configurable uplift to treated invoices in the promo month.
   - Use a permutation test on the mean to estimate a p-value.
   - Report effect size + practical significance.

2) Cycle time test (before/after):
   - Compute AP "days-to-pay" per invoice from invoice and payment events.
   - Choose a changeover date at the median invoice date.
   - Apply a small, configurable reduction to the "after" group to represent a process
     improvement.
   - Use a permutation test on the mean.

Outputs are deterministic for a given seed (stable file names, JSON summary, memo,
figure manifest, and charts following the repo's style contract)."""

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
    plot_bar,
    plot_histogram_with_markers,
    save_figure,
    style_context,
)


DEFAULT_CONFIDENCE = 0.95
DEFAULT_N_PERM = 2_000

# Teaching knobs (keep small; emphasize effect size, not p-values)
DEFAULT_PROMO_UPLIFT_PCT = 0.08
DEFAULT_CYCLE_TIME_REDUCTION_DAYS = 2.0


@dataclass(frozen=True)
class Ch12Outputs:
    figures_dir: Path
    figure_paths: list[Path]
    manifest_path: Path
    memo_path: Path
    design_path: Path
    summary_path: Path


def _read_csv_required(datadir: Path, filename: str) -> pd.DataFrame:
    path = Path(datadir) / filename
    if not path.exists():
        raise FileNotFoundError(f"Required input missing: {path}")
    return pd.read_csv(path)


def _as_month(series: pd.Series) -> pd.Series:
    # Keep month as YYYY-MM for stable grouping.
    dt = pd.to_datetime(series, errors="coerce")
    return dt.dt.to_period("M").astype(str)


def _assign_customers_to_groups(
    customers: list[str], *, rng: np.random.Generator, treated_fraction: float = 0.5
) -> dict[str, str]:
    """Deterministically assign customers to "treatment" or "control"."""
    cust = sorted(set(str(c) for c in customers))
    n = len(cust)
    if n == 0:
        return {}

    n_treat = int(round(n * float(treated_fraction)))
    # Deterministic: shuffle with RNG derived from seed.
    idx = np.arange(n)
    rng.shuffle(idx)
    treat_idx = set(idx[:n_treat].tolist())
    return {cust[i]: ("treatment" if i in treat_idx else "control") for i in range(n)}


def _mean_diff(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(x) - np.mean(y))


def _cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    # Pooled SD (unbiased). Return NaN if degenerate.
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx, ny = x.size, y.size
    if nx < 2 or ny < 2:
        return float("nan")
    vx = np.var(x, ddof=1)
    vy = np.var(y, ddof=1)
    pooled = ((nx - 1) * vx + (ny - 1) * vy) / float(nx + ny - 2)
    if not np.isfinite(pooled) or pooled <= 0:
        return float("nan")
    return float((np.mean(x) - np.mean(y)) / np.sqrt(pooled))


def _bootstrap_mean_diff(
    x: np.ndarray, y: np.ndarray, *, rng: np.random.Generator, n_boot: int = 2_000
) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx, ny = x.size, y.size
    if nx == 0 or ny == 0:
        return np.array([], dtype=float)

    # Bootstrap within each group.
    bx = rng.integers(0, nx, size=(n_boot, nx))
    by = rng.integers(0, ny, size=(n_boot, ny))
    diffs = np.mean(x[bx], axis=1) - np.mean(y[by], axis=1)
    return diffs.astype(float)


def _ci_from_samples(samples: np.ndarray, confidence: float) -> tuple[float, float]:
    if samples.size == 0:
        return float("nan"), float("nan")
    alpha = 1.0 - float(confidence)
    lo = float(np.quantile(samples, alpha / 2.0))
    hi = float(np.quantile(samples, 1.0 - alpha / 2.0))
    return lo, hi


def _permutation_test_mean_diff(
    x: np.ndarray, y: np.ndarray, *, rng: np.random.Generator, n_perm: int = DEFAULT_N_PERM
) -> tuple[float, np.ndarray]:
    """Two-sided permutation test for difference in means."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx, ny = x.size, y.size
    if nx == 0 or ny == 0:
        return float("nan"), np.array([], dtype=float)

    observed = _mean_diff(x, y)
    pooled = np.concatenate([x, y])
    n = pooled.size

    diffs = np.empty(int(n_perm), dtype=float)
    for i in range(int(n_perm)):
        perm = np.arange(n)
        rng.shuffle(perm)
        x_p = pooled[perm[:nx]]
        y_p = pooled[perm[nx:]]
        diffs[i] = _mean_diff(x_p, y_p)

    # Add-one smoothing.
    p = (1.0 + float(np.sum(np.abs(diffs) >= abs(observed)))) / (float(n_perm) + 1.0)
    return float(p), diffs


def analyze_ch12(
    *,
    datadir: Path,
    outdir: Path | None,
    seed: int = 123,
    confidence: float = DEFAULT_CONFIDENCE,
    n_perm: int = DEFAULT_N_PERM,
    promo_uplift_pct: float = DEFAULT_PROMO_UPLIFT_PCT,
    cycle_time_reduction_days: float = DEFAULT_CYCLE_TIME_REDUCTION_DAYS,
) -> Ch12Outputs:
    """Run Chapter 12 analysis and write deterministic artifacts."""

    apply_seed(seed)

    if outdir is None:
        outdir = Path("outputs/track_d")
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    design_path = outdir / "ch12_experiment_design.json"
    summary_path = outdir / "ch12_hypothesis_testing_summary.json"
    memo_path = outdir / "ch12_experiment_memo.md"
    manifest_path = outdir / "ch12_figures_manifest.csv"

    rng = np.random.default_rng(int(seed) + 12_000)

    # -------------------- Case 1: Promotion test (AR invoices) --------------------
    ar = _read_csv_required(datadir, "ar_events.csv")
    required_cols = {"event_type", "customer", "invoice_id", "amount", "date"}
    if ar.empty or not required_cols.issubset(set(ar.columns)):
        raise ValueError(f"ar_events.csv must contain columns: {sorted(required_cols)}")

    inv = ar.loc[ar["event_type"].astype(str) == "invoice", ["date", "customer", "invoice_id", "amount"]].copy()
    inv["month"] = _as_month(inv["date"])

    # Choose the month with the most invoices (ensures sample size).
    if inv.empty:
        raise ValueError("No AR invoice events found to construct promotion case.")
    promo_month = str(inv["month"].value_counts().idxmax())

    cust_to_group = _assign_customers_to_groups(inv["customer"].astype(str).tolist(), rng=rng)
    inv["group"] = inv["customer"].astype(str).map(cust_to_group).fillna("control")

    promo = inv.loc[inv["month"] == promo_month].copy()
    promo["amount"] = pd.to_numeric(promo["amount"], errors="coerce")
    promo = promo.dropna(subset=["amount"]).copy()

    # Teaching: apply uplift to treated amounts during the promo month.
    promo["amount_adjusted"] = promo["amount"]
    promo.loc[promo["group"] == "treatment", "amount_adjusted"] = promo.loc[
        promo["group"] == "treatment", "amount"
    ] * (1.0 + float(promo_uplift_pct))

    x = promo.loc[promo["group"] == "treatment", "amount_adjusted"].to_numpy(dtype=float)
    y = promo.loc[promo["group"] == "control", "amount_adjusted"].to_numpy(dtype=float)

    promo_p_value, promo_perm_diffs = _permutation_test_mean_diff(x, y, rng=rng, n_perm=int(n_perm))
    promo_obs_diff = _mean_diff(x, y)
    promo_cohen_d = _cohens_d(x, y)

    promo_boot_diffs = _bootstrap_mean_diff(x, y, rng=rng, n_boot=2_000)
    promo_ci_low, promo_ci_high = _ci_from_samples(promo_boot_diffs, float(confidence))

    promo_control_mean = float(np.mean(y)) if y.size else float("nan")
    promo_rel_lift = float(promo_obs_diff / promo_control_mean) if np.isfinite(promo_control_mean) and promo_control_mean != 0 else float("nan")

    # -------------------- Case 2: Cycle time test (AP days-to-pay) --------------------
    ap = _read_csv_required(datadir, "ap_events.csv")
    required_cols = {"event_type", "invoice_id", "amount", "date"}
    if ap.empty or not required_cols.issubset(set(ap.columns)):
        raise ValueError(f"ap_events.csv must contain columns: {sorted(required_cols)}")

    ap = ap[["event_type", "invoice_id", "amount", "date"]].copy()
    ap["date"] = pd.to_datetime(ap["date"], errors="coerce")

    ap["month"] = ap["date"].dt.to_period("M").astype(str)

    inv_rows = ap.loc[
        ap["event_type"].astype(str) == "invoice",
        ["invoice_id", "month", "date", "amount"],
    ].rename(columns={"date": "invoice_date", "amount": "invoice_amount"})

    # In NSO v1 the payment events are modeled at the month level (not per-invoice),
    # so we map each invoice to the *latest* payment date in its invoice month.
    pay_rows = ap.loc[
        ap["event_type"].astype(str) == "payment",
        ["month", "date"],
    ].rename(columns={"date": "payment_date"})

    pay_by_month = pay_rows.groupby("month", as_index=False)["payment_date"].max()

    lags = inv_rows.merge(pay_by_month, on="month", how="left")
    lags = lags.dropna(subset=["invoice_date", "payment_date"]).copy()
    lags["days_to_pay"] = (lags["payment_date"] - lags["invoice_date"]).dt.days.astype(float)
    lags["days_to_pay"] = np.maximum(0.0, lags["days_to_pay"].to_numpy(dtype=float))

    if lags.empty:
        raise ValueError("No AP invoices with a month-level payment date found to compute cycle time.")

    changeover_date = lags["invoice_date"].median()
    lags["period"] = np.where(lags["invoice_date"] < changeover_date, "before", "after")

    # Teaching: apply a small reduction to the after-period cycle time.
    lags["days_to_pay_adjusted"] = lags["days_to_pay"]
    lags.loc[lags["period"] == "after", "days_to_pay_adjusted"] = np.maximum(
        0.0,
        lags.loc[lags["period"] == "after", "days_to_pay"].to_numpy(dtype=float) - float(cycle_time_reduction_days),
    )

    xb = lags.loc[lags["period"] == "before", "days_to_pay_adjusted"].to_numpy(dtype=float)
    ya = lags.loc[lags["period"] == "after", "days_to_pay_adjusted"].to_numpy(dtype=float)

    # We report (before - after) so a positive diff means improvement.
    cycle_p_value, cycle_perm_diffs = _permutation_test_mean_diff(xb, ya, rng=rng, n_perm=int(n_perm))
    cycle_obs_diff = _mean_diff(xb, ya)
    cycle_cohen_d = _cohens_d(xb, ya)

    cycle_boot_diffs = _bootstrap_mean_diff(xb, ya, rng=rng, n_boot=2_000)
    cycle_ci_low, cycle_ci_high = _ci_from_samples(cycle_boot_diffs, float(confidence))

    # -------------------- Design (pre-commitment) --------------------
    design = {
        "chapter": "business_ch12_hypothesis_testing_decisions",
        "seed": int(seed),
        "confidence": float(confidence),
        "test": "two-sided permutation test on mean difference",
        "n_perm": int(n_perm),
        "precommitment": {
            "alpha": float(1.0 - float(confidence)),
            "stopping_rule": "Run exactly n_perm permutations; do not peek and stop early.",
            "primary_metrics": {
                "promotion": "Average invoice amount (AR) in promo month",
                "cycle_time": "Days-to-pay (AP) per invoice",
            },
            "decision_rule": {
                "promotion": "Consider rollout if p < alpha AND effect size is practically meaningful.",
                "cycle_time": "Consider full deployment if p < alpha AND average days saved justifies costs.",
            },
        },
        "teaching_knobs": {
            "promo_month": promo_month,
            "promo_uplift_pct": float(promo_uplift_pct),
            "cycle_time_reduction_days": float(cycle_time_reduction_days),
            "note": "Knobs inject a small effect so examples are non-trivial; set to 0 for a pure 'measurement-only' run.",
        },
    }
    design_path.write_text(json.dumps(design, indent=2), encoding="utf-8")

    # -------------------- Figures + manifest --------------------
    manifest: list[FigureManifestRow] = []
    figure_paths: list[Path] = []

    # Figure 1: Bar chart of mean cycle time before vs after
    cycle_means = (
        lags.groupby("period", observed=True)["days_to_pay_adjusted"].mean().reindex(["before", "after"]).reset_index()
    )
    cycle_means = cycle_means.rename(columns={"period": "group", "days_to_pay_adjusted": "mean_days"})

    with style_context():
        fig1 = plot_bar(
            df=cycle_means,
            x="group",
            y="mean_days",
            title="AP cycle time (mean days-to-pay): before vs after change",
            x_label="Period",
            y_label="Mean days-to-pay",
        )
    path1 = figures_dir / "ch12_cycle_time_means_bar.png"
    save_figure(fig1, path1, FigureSpec(chart_type="bar", title="AP cycle time mean (before vs after)"))
    figure_paths.append(path1)
    manifest.append(
        FigureManifestRow(
            filename=path1.name,
            chart_type="bar",
            title="AP cycle time (mean days-to-pay): before vs after change",
            x_label="Period",
            y_label="Mean days-to-pay",
            guardrail_note="Bar chart starts at zero; report effect size and CI in the memo.",
            data_source="Computed from ap_events.csv invoice/payment pairs (with a small teaching adjustment).",
        )
    )

    # Figure 2: Histogram of bootstrap mean differences for promotion test
    with style_context():
        fig2 = plot_histogram_with_markers(
            values=pd.Series(promo_boot_diffs),
            title=f"Promotion test: bootstrap distribution of mean AOV difference (promo month {promo_month})",
            x_label="Mean difference (treatment - control)",
            y_label="Frequency",
            markers={"No effect": 0.0, "Observed": promo_obs_diff},
        )
    path2 = figures_dir / "ch12_promo_bootstrap_hist.png"
    save_figure(fig2, path2, FigureSpec(chart_type="histogram", title="Promotion effect (bootstrap mean diff)"))
    figure_paths.append(path2)
    manifest.append(
        FigureManifestRow(
            filename=path2.name,
            chart_type="histogram",
            title=f"Promotion test: bootstrap distribution of mean AOV difference (promo month {promo_month})",
            x_label="Mean difference (treatment - control)",
            y_label="Frequency",
            guardrail_note="Do not over-interpret the tail; pair p-value with effect size and a practical threshold.",
            data_source="Derived from ar_events.csv invoices; treatment group gets a small uplift for teaching.",
        )
    )

    manifest_df = pd.DataFrame([m.__dict__ for m in manifest])
    manifest_df.to_csv(manifest_path, index=False)

    # -------------------- Summary JSON --------------------
    summary: dict[str, Any] = {
        "chapter": "business_ch12_hypothesis_testing_decisions",
        "seed": int(seed),
        "confidence": float(confidence),
        "promotion_test": {
            "promo_month": promo_month,
            "uplift_pct_assumed": float(promo_uplift_pct),  # <-- ADD THIS LINE
            "n_treatment": int(x.size),
            "n_control": int(y.size),
            "mean_treatment": float(np.mean(x)) if x.size else float("nan"),
            "mean_control": float(np.mean(y)) if y.size else float("nan"),
            "mean_diff": float(promo_obs_diff),
            "relative_lift": float(promo_rel_lift),
            "ci_low": float(promo_ci_low),
            "ci_high": float(promo_ci_high),
            "p_value": float(promo_p_value),
            "cohens_d": float(promo_cohen_d),
            "n_perm": int(n_perm),
            "note": "Permutation p-value on mean difference (two-sided).",
        },
        "cycle_time_test": {
            "changeover_date": str(pd.to_datetime(changeover_date).date()),
            "reduction_days_assumed": float(cycle_time_reduction_days),  # <-- ADD THIS LINE
            "n_before": int(xb.size),
            "n_after": int(ya.size),
            "mean_before": float(np.mean(xb)) if xb.size else float("nan"),
            "mean_after": float(np.mean(ya)) if ya.size else float("nan"),
            "mean_days_saved": float(cycle_obs_diff),
            "ci_low": float(cycle_ci_low),
            "ci_high": float(cycle_ci_high),
            "p_value": float(cycle_p_value),
            "cohens_d": float(cycle_cohen_d),
            "n_perm": int(n_perm),
            "note": "Permutation p-value on (before - after) mean days-to-pay (two-sided).",
        },

        "p_hacking_guardrails": {
            "precommitment_file": design_path.name,
            "rules": [
                "Fix your metric and alpha before you look at results.",
                "Avoid stopping early because the p-value looks good.",
                "Report effect size + CI; don't treat p < alpha as the only success criterion.",
                "If you test many metrics, adjust or declare one primary metric.",
            ],
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # -------------------- Audit-style memo (business language) --------------------
    alpha = 1.0 - float(confidence)

    def _fmt_pct(v: float) -> str:
        if not np.isfinite(v):
            return "NA"
        return f"{100.0 * v:.1f}%"

    def _fmt_days(v: float) -> str:
        if not np.isfinite(v):
            return "NA"
        return f"{v:.2f} days"

    def _fmt_money(v: float) -> str:
        if not np.isfinite(v):
            return "NA"
        return f"${v:,.2f}"

    memo_lines = [
        "# Chapter 12 — Experiment Results Memo (Hypothesis Testing for Decisions)",
        "",
        "## Pre-commitment (anti p-hacking)",
        f"- Confidence level: {confidence:.2f} (alpha = {alpha:.2f})",
        f"- Test: two-sided permutation test on mean difference (n_perm = {int(n_perm)})",
        "- Decision rule: require both (a) statistical evidence (p < alpha) and (b) practical significance.",
        "",
        "## Case 1 — Promotion Test (A/B style)",
        f"- Promo month selected (most invoices): {promo_month}",
        f"- Treatment vs control sample sizes: n_treat={int(x.size)}, n_control={int(y.size)}",
        f"- Mean invoice amount: treat={_fmt_money(float(np.mean(x)) if x.size else float('nan'))}, control={_fmt_money(float(np.mean(y)) if y.size else float('nan'))}",
        f"- Effect (mean diff): {_fmt_money(promo_obs_diff)} (lift: {_fmt_pct(promo_rel_lift)})",
        f"- {confidence:.0%} bootstrap CI for mean diff: [{_fmt_money(promo_ci_low)}, {_fmt_money(promo_ci_high)}]",
        f"- p-value: {promo_p_value:.4f} ; Cohen's d: {promo_cohen_d:.2f}",
        "- Business read: if lift is small (or CI crosses 0), the promo may not be worth the operational cost.",
        "",
        "## Case 2 — AP Cycle Time (before/after change)",
        f"- Changeover date (median invoice date): {str(pd.to_datetime(changeover_date).date())}",
        f"- Sample sizes: n_before={int(xb.size)}, n_after={int(ya.size)}",
        f"- Mean days-to-pay: before={_fmt_days(float(np.mean(xb)) if xb.size else float('nan'))}, after={_fmt_days(float(np.mean(ya)) if ya.size else float('nan'))}",
        f"- Estimated days saved (before - after): {_fmt_days(cycle_obs_diff)}",
        f"- {confidence:.0%} bootstrap CI for days saved: [{_fmt_days(cycle_ci_low)}, {_fmt_days(cycle_ci_high)}]",
        f"- p-value: {cycle_p_value:.4f} ; Cohen's d: {cycle_cohen_d:.2f}",
        "- Business read: translate days saved into dollars (labor time + vendor terms + late-fee risk).",
        "",
        "## Notes / guardrails",
        "- p-values answer: \"Is this signal likely under 'no effect'?\" They do *not* answer: \"Is it worth doing?\"",
        "- Effect sizes + confidence intervals are the bridge from statistics to decisions.",
        "- If you test multiple metrics (AOV, conversion, churn...), pick one primary metric upfront.",
        "",
    ]
    memo_path.write_text("\n".join(memo_lines), encoding="utf-8")

    return Ch12Outputs(
        figures_dir=figures_dir,
        figure_paths=figure_paths,
        manifest_path=manifest_path,
        memo_path=memo_path,
        design_path=design_path,
        summary_path=summary_path,
    )


def main(argv: list[str] | None = None) -> int:
    p = base_parser("Business Ch12: hypothesis testing for decisions (A/B + before/after)")
    p.add_argument("--datadir", type=Path, required=True, help="Path to NSO v1 dataset folder")
    p.add_argument("--confidence", type=float, default=DEFAULT_CONFIDENCE)
    p.add_argument("--n-perm", type=int, default=DEFAULT_N_PERM)
    p.add_argument("--promo-uplift-pct", type=float, default=DEFAULT_PROMO_UPLIFT_PCT)
    p.add_argument("--cycle-time-reduction-days", type=float, default=DEFAULT_CYCLE_TIME_REDUCTION_DAYS)
    args = p.parse_args(argv)

    analyze_ch12(
        datadir=Path(args.datadir),
        outdir=Path(args.outdir),
        seed=int(args.seed) if args.seed is not None else 123,
        confidence=float(args.confidence),
        n_perm=int(args.n_perm),
        promo_uplift_pct=float(args.promo_uplift_pct),
        cycle_time_reduction_days=float(args.cycle_time_reduction_days),
    )

    print(f"Wrote Chapter 12 artifacts -> {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

