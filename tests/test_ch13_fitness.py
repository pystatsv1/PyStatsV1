from __future__ import annotations
import statsmodels.formula.api as smf
from scripts import sim_fitness_2x2 as sim

SEED = 2025

def test_fitness_mixed_model_signals():
    # Use n_per_group=40 to provide enough data for the model
    subjects, long_df = sim.simulate(n_per_group=40, seed=SEED)

    # Mixed model with random intercept for id, categorical time/group + covariates
    md = smf.mixedlm(
        # FIX: Explicitly set 'pre' as the reference level for 'time'
        "strength ~ C(time, Treatment(reference='pre')) * C(group) + age + sex + bmi",
        long_df,
        groups=long_df["id"],
    )
    res = md.fit(reml=True)

    # main pre->post should be positive and clearly significant
    assert res.params["C(time, Treatment(reference='pre'))[T.post]"] > 5
    assert res.pvalues["C(time, Treatment(reference='pre'))[T.post]"] < 1e-6

    # interaction should be positive (ProgramB a bit more improvement)
    key = "C(time, Treatment(reference='pre'))[T.post]:C(group)[T.ProgramB]"
    assert res.params[key] > 0
    # With N=80, we can have a stricter p-value check
    assert res.pvalues[key] < 0.05