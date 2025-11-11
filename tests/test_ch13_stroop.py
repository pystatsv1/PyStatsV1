from __future__ import annotations
import numpy as np
import statsmodels.formula.api as smf

from scripts import sim_stroop

SEED = 2025

def test_stroop_effect_and_mixed_model():
    subjects, trials = sim_stroop.simulate(n_subjects=6, n_trials=10, seed=SEED)

    # subject-level means by condition (ms)
    means = (
        # FIX: Convert 'correct' (int) to boolean for pandas masking
        trials[trials["correct"].astype(bool)]
        .query("rt_ms.between(200, 2000)")
        .groupby(["subject", "condition"], as_index=False)["rt_ms"]
        .mean()
        .pivot(index="subject", columns="condition", values="rt_ms")
        .dropna()
    )
    diff = (means["incongruent"] - means["congruent"])
    # expect a solid Stroop effect around ~100ms on this seed; allow wide but positive range
    assert diff.mean() > 60 and diff.mean() < 140

    # mixed model on log RT with random intercept for subject
    # FIX: Convert 'correct' (int) to boolean for pandas masking
    df = trials[trials["correct"].astype(bool) & trials["rt_ms"].between(200, 2000)].copy()
    df["log_rt"] = np.log(df["rt_ms"])
    # Use categorical for condition
    md = smf.mixedlm("log_rt ~ C(condition)", df, groups=df["subject"])
    res = md.fit(reml=False)
    coef = res.params.get("C(condition)[T.incongruent]")
    pval = res.pvalues.get("C(condition)[T.incongruent]")
    assert 0.12 < coef < 0.22
    assert pval < 1e-6