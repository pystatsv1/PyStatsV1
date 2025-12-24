# SPDX-License-Identifier: MIT
# business_ch11_sampling_estimation_audit_controls.py
"""Track D — Business Statistics & Forecasting for Accountants.

Chapter 11: Sampling and Estimation (Audit and Controls Lens)

Accountants often review thousands of transactions. Sampling is a cost-effective control
only when it is (1) explicit, (2) risk-based, and (3) communicated with uncertainty.

This chapter produces deterministic, audit-friendly artifacts:
- a stratified sampling plan (material items 100% + random samples for the long tail)
- an error-rate confidence interval (Wilson) with plain-language interpretation
- a short memo using audit vocabulary (population, sample size, materiality, tolerance)

Notes
-----
* This is *not* an external-audit substitute. It is a teaching chapter.
* The NSO v1 dataset does not contain true "control failures", so we simulate an error flag
  deterministically from a seeded RNG to demonstrate CI mechanics.

Outputs are designed to be:
- deterministic (seeded)
- audit-friendly (explicit assumptions + defensible calculations)
- matplotlib-only (no seaborn)
"""

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
    save_figure,
    style_context,
)

# --- Defaults / guardrails (explicit + testable) ---

DEFAULT_CONFIDENCE = 0.95
DEFAULT_TOLERANCE = 0.02  # management tolerance for error rate

DEFAULT_HIGH_VALUE_THRESHOLD = 1000.0  # "material" items -> 100% review
DEFAULT_LOW_VALUE_THRESHOLD = 50.0     # "immaterial" long tail
DEFAULT_LOW_VALUE_RATE = 0.05          # sample 5% of low-value items
DEFAULT_MID_VALUE_RATE = 0.10          # sample 10% of mid-value items (teaching default)

# Simulation of control failures (teaching device)
_BASE_ERROR_P = 0.01
_HIGH_VALUE_ERROR_BONUS = 0.01
_LOW_VALUE_ERROR_BONUS = 0.005


@dataclass(frozen=True)
class Ch11Outputs:
    sampling_plan_path: Path
    memo_path: Path
    summary_path: Path
    manifest_path: Path
    figures_dir: Path
    figure_paths: list[Path]


def _read_csv_required(datadir: Path, fname: str) -> pd.DataFrame:
    path = datadir / fname
    if not path.exists():
        raise FileNotFoundError(f"Missing required dataset file: {path}")
    return pd.read_csv(path)


def _z_for_confidence(confidence: float) -> float:
    """Return a z critical value for common confidence levels.

    We keep this explicit (audit-friendly) and avoid extra dependencies.
    """
    c = float(confidence)
    if np.isclose(c, 0.90):
        return 1.6448536269514722
    if np.isclose(c, 0.95):
        return 1.959963984540054
    if np.isclose(c, 0.99):
        return 2.5758293035489004
    raise ValueError("confidence must be one of: 0.90, 0.95, 0.99")


def proportion_ci_wilson(k: int, n: int, confidence: float = DEFAULT_CONFIDENCE) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (k/n).

    Returns (low, high) in [0, 1]. If n==0 -> (nan, nan).
    """
    n = int(n)
    k = int(k)
    if n <= 0:
        return (float("nan"), float("nan"))

    z = _z_for_confidence(confidence)
    phat = k / n
    denom = 1.0 + (z**2) / n
    center = (phat + (z**2) / (2.0 * n)) / denom
    half = (z * np.sqrt((phat * (1.0 - phat) + (z**2) / (4.0 * n)) / n)) / denom

    low = max(0.0, float(center - half))
    high = min(1.0, float(center + half))
    return (low, high)


def _risk_based_sample(
    invoices: pd.DataFrame,
    *,
    rng: np.random.Generator,
    high_value_threshold: float,
    low_value_threshold: float,
    low_value_rate: float,
    mid_value_rate: float,
    id_col: str = "invoice_id",
    amount_col: str = "amount",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a sampled invoice table and a sampling-plan dict.

    Stratification:
    - high_value (>= high_value_threshold): 100% selection (materiality)
    - low_value (< low_value_threshold): random sample at low_value_rate
    - mid_value (else): random sample at mid_value_rate
    """
    required = {id_col, amount_col}
    if not required.issubset(set(invoices.columns)):
        raise ValueError(f"invoices must include columns: {sorted(required)}")

    df = invoices[[id_col, amount_col]].copy()
    df[id_col] = df[id_col].astype(str)
    df[amount_col] = df[amount_col].astype(float)

    df = df[df[amount_col].notna()].copy()
    df = df[df[amount_col] > 0].copy()

    def _stratum(a: float) -> str:
        if a >= float(high_value_threshold):
            return "high_value"
        if a < float(low_value_threshold):
            return "low_value"
        return "mid_value"

    df["stratum"] = df[amount_col].map(_stratum)

    # Determine selection counts (deterministic given seed + sort)
    df = df.sort_values(["stratum", id_col], kind="mergesort").reset_index(drop=True)

    selected_ids: set[str] = set()

    # High value: include all
    high = df[df["stratum"] == "high_value"]
    selected_ids.update(high[id_col].tolist())

    # Mid and low: random sample without replacement
    for stratum, rate in [("mid_value", mid_value_rate), ("low_value", low_value_rate)]:
        g = df[df["stratum"] == stratum]
        n = int(g.shape[0])
        k = int(np.floor(n * float(rate)))
        k = max(0, min(n, k))
        if k > 0:
            choices = rng.choice(g[id_col].to_numpy(dtype=str), size=k, replace=False)
            selected_ids.update([str(x) for x in choices])

    df["selected"] = df[id_col].isin(selected_ids)

    plan = {
        "population_n": int(df.shape[0]),
        "sample_n": int(df["selected"].sum()),
        "params": {
            "high_value_threshold": float(high_value_threshold),
            "low_value_threshold": float(low_value_threshold),
            "low_value_rate": float(low_value_rate),
            "mid_value_rate": float(mid_value_rate),
        },
        "strata": {
            "high_value": {
                "population_n": int((df["stratum"] == "high_value").sum()),
                "sample_n": int(((df["stratum"] == "high_value") & df["selected"]).sum()),
            },
            "mid_value": {
                "population_n": int((df["stratum"] == "mid_value").sum()),
                "sample_n": int(((df["stratum"] == "mid_value") & df["selected"]).sum()),
            },
            "low_value": {
                "population_n": int((df["stratum"] == "low_value").sum()),
                "sample_n": int(((df["stratum"] == "low_value") & df["selected"]).sum()),
            },
        },
        "selected_invoice_ids": df.loc[df["selected"], id_col].tolist(),
    }

    return df, plan


def _simulate_control_errors(
    sampled: pd.DataFrame,
    *,
    rng: np.random.Generator,
    amount_col: str = "amount",
) -> np.ndarray:
    """Deterministically simulate control failures for CI demonstration."""
    a = sampled[amount_col].astype(float).to_numpy()
    # small risk uplift for very large items and tiny items (more process variation)
    p = (
        _BASE_ERROR_P
        + _HIGH_VALUE_ERROR_BONUS * (a >= DEFAULT_HIGH_VALUE_THRESHOLD)
        + _LOW_VALUE_ERROR_BONUS * (a < DEFAULT_LOW_VALUE_THRESHOLD)
    )
    p = np.clip(p.astype(float), 0.0, 1.0)
    return rng.random(size=a.shape[0]) < p


def _make_audit_memo(
    *,
    population_n: int,
    sample_n: int,
    confidence: float,
    tolerance: float,
    k_errors: int,
    ci_low: float,
    ci_high: float,
    high_value_threshold: float,
    low_value_threshold: float,
    low_value_rate: float,
    mid_value_rate: float,
    worked_example: dict[str, Any],
) -> str:
    """Return a short deterministic memo (markdown)."""
    lines: list[str] = []

    lines.append(
        "We designed a risk-based sampling plan for invoice review. "
        f"Population size: {population_n} invoices. Sample size: {sample_n} invoices."
    )

    lines.append(
        f"Materiality rule: reviewed 100% of items ≥ ${high_value_threshold:,.0f}. "
        f"For the long tail, we randomly sampled {mid_value_rate:.0%} of $[{low_value_threshold:,.0f}, {high_value_threshold:,.0f}) "
        f"and {low_value_rate:.0%} of items < ${low_value_threshold:,.0f}. "
        "This stratification concentrates effort where risk and impact are highest."
    )

    phat = (k_errors / sample_n) if sample_n > 0 else float("nan")
    lines.append(
        f"Observed error rate in the sample: {phat:.1%} ({k_errors} errors / {sample_n} reviewed). "
        f"Using a {confidence:.0%} Wilson confidence interval, the true population error rate is plausibly between {ci_low:.1%} and {ci_high:.1%}."
    )

    decision = "PASS" if (np.isfinite(ci_high) and ci_high <= float(tolerance)) else "FAIL / INVESTIGATE"
    lines.append(
        f"Control decision vs tolerance ({tolerance:.1%}): {decision}. "
        "Controls lens: if the CI upper bound exceeds tolerance, we cannot claim the process meets the threshold at the stated confidence."
    )

    # Worked example (problem statement)
    we = worked_example
    lines.append(
        f"Worked example (inventory counts): {we['k_errors']} errors in {we['n']} counts -> {we['phat']:.1%} observed. "
        f"{we['confidence']:.0%} CI: [{we['ci_low']:.1%}, {we['ci_high']:.1%}] vs tolerance {we['tolerance']:.1%} -> {we['decision']}."
    )

    lines.append(
        "Assumptions: random sampling within strata; items are treated as independent; the interval describes uncertainty from sampling, not all forms of risk (fraud, collusion, data loss). "
        "If the population changes materially (new vendors, new system), re-baseline the plan."
    )

    return "\n\n".join(lines) + "\n"


def analyze_ch11(
    *,
    datadir: Path,
    outdir: Path | None,
    seed: int = 123,
    confidence: float = DEFAULT_CONFIDENCE,
    tolerance: float = DEFAULT_TOLERANCE,
    high_value_threshold: float = DEFAULT_HIGH_VALUE_THRESHOLD,
    low_value_threshold: float = DEFAULT_LOW_VALUE_THRESHOLD,
    low_value_rate: float = DEFAULT_LOW_VALUE_RATE,
    mid_value_rate: float = DEFAULT_MID_VALUE_RATE,
) -> Ch11Outputs:
    """Run Chapter 11 analysis and write deterministic artifacts."""
    apply_seed(seed)

    if outdir is None:
        outdir = Path("outputs/track_d")
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    figures_dir = outdir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    sampling_plan_path = outdir / "ch11_sampling_plan.json"
    summary_path = outdir / "ch11_sampling_summary.json"
    memo_path = outdir / "ch11_audit_memo.md"
    manifest_path = outdir / "ch11_figures_manifest.csv"

    # --- Inputs: treat AP invoice rows as the audit population ---
    ap = _read_csv_required(datadir, "ap_events.csv")
    if ap.empty or not {"event_type", "invoice_id", "amount"}.issubset(set(ap.columns)):
        raise ValueError("ap_events.csv must contain columns: event_type, invoice_id, amount")

    invoices = ap.loc[ap["event_type"].astype(str) == "invoice", ["invoice_id", "amount"]].copy()

    rng = np.random.default_rng(int(seed) + 11_000)

    sampled_df, plan = _risk_based_sample(
        invoices,
        rng=rng,
        high_value_threshold=float(high_value_threshold),
        low_value_threshold=float(low_value_threshold),
        low_value_rate=float(low_value_rate),
        mid_value_rate=float(mid_value_rate),
    )
    sampling_plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    # --- Simulate control failures on the selected sample (teaching) ---
    sample = sampled_df.loc[sampled_df["selected"]].copy()
    error_flags = _simulate_control_errors(sample, rng=rng, amount_col="amount")
    k_errors = int(np.sum(error_flags))
    n = int(sample.shape[0])

    ci_low, ci_high = proportion_ci_wilson(k=k_errors, n=n, confidence=float(confidence))

    # Worked example from the vision document (n=50, k=2)
    ex_n = 50
    ex_k = 2
    ex_low, ex_high = proportion_ci_wilson(k=ex_k, n=ex_n, confidence=float(confidence))
    ex_phat = ex_k / ex_n
    ex_decision = "PASS" if (np.isfinite(ex_high) and ex_high <= float(tolerance)) else "FAIL / INVESTIGATE"
    worked_example = {
        "n": int(ex_n),
        "k_errors": int(ex_k),
        "phat": float(ex_phat),
        "confidence": float(confidence),
        "ci_low": float(ex_low),
        "ci_high": float(ex_high),
        "tolerance": float(tolerance),
        "decision": ex_decision,
    }

    # --- Figures + manifest (style contract) ---
    manifest: list[FigureManifestRow] = []
    figure_paths: list[Path] = []

    # Figure 1: population vs sample by stratum
    strata = ["high_value", "mid_value", "low_value"]
    pop_counts = [int((sampled_df["stratum"] == s).sum()) for s in strata]

    pop_df_plot = pd.DataFrame({"stratum": strata, "count": pop_counts})

    with style_context():
        fig = plot_bar(
            df=pop_df_plot,
            x="stratum",
            y="count",
            title="Invoice population by stratum (for sampling)",
            x_label="Stratum",
            y_label="Count",
        )
        path = figures_dir / "ch11_strata_sampling_bar.png"
        save_figure(fig, path, FigureSpec(chart_type="bar", title="Invoice population by stratum"))
    manifest.append(
        FigureManifestRow(
            filename=path.name,
            chart_type="bar",
            title="Invoice population by stratum (for sampling)",
            x_label="Stratum",
            y_label="Count",
            guardrail_note="Bar chart starts at zero; strata are explicit to avoid cherry-picking.",
            data_source="ap_events.csv (invoice rows)",
        )
    )
    figure_paths.append(path)

    # Figure 2: error rate CI (simple bar + whisker)
    import matplotlib.pyplot as plt

    phat = (k_errors / n) if n > 0 else float("nan")
    with style_context():
        fig, ax = plt.subplots()
        ax.bar([0], [phat])
        if np.isfinite(ci_low) and np.isfinite(ci_high):
            ax.errorbar([0], [phat], yerr=[[phat - ci_low], [ci_high - phat]], fmt="none", capsize=6)
        ax.set_xticks([0])
        ax.set_xticklabels(["observed"])
        ax.set_ylim(0, max(0.05, float(ci_high) * 1.2 if np.isfinite(ci_high) else 0.05))
        ax.set_title(f"Sample error rate with {confidence:.0%} CI (Wilson)")
        ax.set_ylabel("Error rate")
        ax.set_xlabel(" ")
        ax.grid(True, axis="y", alpha=0.2)
        fig.tight_layout()
        path2 = figures_dir / "ch11_error_rate_ci.png"
        save_figure(fig, path2, FigureSpec(chart_type="scatter", title="Sample error rate with CI"))
    manifest.append(
        FigureManifestRow(
            filename=path2.name,
            chart_type="scatter",
            title=f"Sample error rate with {confidence:.0%} CI (Wilson)",
            x_label="",
            y_label="Error rate",
            guardrail_note="CI communicates sampling uncertainty; do not interpret a point estimate as certainty.",
            data_source="ap_events.csv (sample) + simulated error flags (teaching)",
        )
    )
    figure_paths.append(path2)

    pd.DataFrame([m.__dict__ for m in manifest]).to_csv(manifest_path, index=False)

    memo = _make_audit_memo(
        population_n=int(plan["population_n"]),
        sample_n=int(plan["sample_n"]),
        confidence=float(confidence),
        tolerance=float(tolerance),
        k_errors=int(k_errors),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        high_value_threshold=float(high_value_threshold),
        low_value_threshold=float(low_value_threshold),
        low_value_rate=float(low_value_rate),
        mid_value_rate=float(mid_value_rate),
        worked_example=worked_example,
    )
    memo_path.write_text(memo, encoding="utf-8")

    summary: dict[str, Any] = {
        "chapter": "business_ch11_sampling_estimation_audit_controls",
        "seed": int(seed),
        "inputs": {"datadir": str(datadir), "files": ["ap_events.csv"]},
        "sampling": plan,
        "ci": {
            "confidence": float(confidence),
            "method": "wilson",
            "sample_n": int(n),
            "k_errors": int(k_errors),
            "phat": float(phat) if np.isfinite(phat) else float("nan"),
            "ci_low": float(ci_low),
            "ci_high": float(ci_high),
            "tolerance": float(tolerance),
            "decision": "PASS" if (np.isfinite(ci_high) and ci_high <= float(tolerance)) else "FAIL / INVESTIGATE",
        },
        "worked_example": worked_example,
        "paths": {
            "sampling_plan": str(sampling_plan_path),
            "summary": str(summary_path),
            "memo": str(memo_path),
            "manifest": str(manifest_path),
            "figures_dir": str(figures_dir),
        },
        "figures": [p.name for p in figure_paths],
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return Ch11Outputs(
        sampling_plan_path=sampling_plan_path,
        memo_path=memo_path,
        summary_path=summary_path,
        manifest_path=manifest_path,
        figures_dir=figures_dir,
        figure_paths=figure_paths,
    )


def main(argv: list[str] | None = None) -> int:
    p = base_parser("Business Ch11: sampling and estimation (audit/controls)")
    p.add_argument("--datadir", type=Path, required=True, help="Path to NSO v1 dataset folder")
    p.add_argument("--confidence", type=float, default=DEFAULT_CONFIDENCE, help="CI confidence (0.90, 0.95, 0.99)")
    p.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE, help="Management tolerance for error rate")
    p.add_argument("--high-value-threshold", type=float, default=DEFAULT_HIGH_VALUE_THRESHOLD)
    p.add_argument("--low-value-threshold", type=float, default=DEFAULT_LOW_VALUE_THRESHOLD)
    p.add_argument("--low-value-rate", type=float, default=DEFAULT_LOW_VALUE_RATE)
    p.add_argument("--mid-value-rate", type=float, default=DEFAULT_MID_VALUE_RATE)
    args = p.parse_args(argv)

    analyze_ch11(
        datadir=Path(args.datadir),
        outdir=Path(args.outdir),
        seed=int(args.seed) if args.seed is not None else 123,
        confidence=float(args.confidence),
        tolerance=float(args.tolerance),
        high_value_threshold=float(args.high_value_threshold),
        low_value_threshold=float(args.low_value_threshold),
        low_value_rate=float(args.low_value_rate),
        mid_value_rate=float(args.mid_value_rate),
    )
    print(f"Wrote Chapter 11 artifacts -> {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
