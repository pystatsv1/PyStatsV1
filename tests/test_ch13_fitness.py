import statsmodels.formula.api as smf
from scripts import sim_fitness_2x2 as sim

SEED = 2025

def test_fitness_mixed_model_signals():
    subjects, long_df = sim.simulate(n_per_group=5, seed=SEED)

    # Mixed model with random intercept for id, categorical time/group + covariates
    md = smf.mixedlm(
        "strength ~ C(time) * C(group) + age + sex + bmi",
        long_df,
        groups=long_df["id"],
    )
    res = md.fit(reml=True)

    # main pre->post should be positive and clearly significant
    assert res.params["C(time)[T.post]"] > 5
    assert res.pvalues["C(time)[T.post]"] < 1e-6

    # interaction should be positive (ProgramB a bit more improvement); allow modest p
    assert res.params["C(time)[T.post]:C(group)[T.ProgramB]"] > 0
    assert res.pvalues["C(time)[T.post]:C(group)[T.ProgramB]"] < 0.2