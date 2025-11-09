# SPDX-License-Identifier: MIT
"""
Simulate trial-level Stroop data (plausible undergrad study).
Creates:
  data/synthetic/psych_stroop_trials.csv
  data/synthetic/psych_stroop_subjects.csv
"""
import os, numpy as np, pandas as pd
rng = np.random.default_rng(42)

N_SUBJ = 60
N_TRIALS_PER_COND = 100
CONDITIONS = ["congruent", "incongruent"]

def simulate():
    os.makedirs("data/synthetic", exist_ok=True)
    # subject-level covariates
    subjects = pd.DataFrame({
        "subject": np.arange(1, N_SUBJ+1),
        "gender": rng.choice(["F","M"], size=N_SUBJ, p=[0.6,0.4]),
        "handedness": rng.choice(["R","L"], size=N_SUBJ, p=[0.9,0.1]),
        # baseline processing speed (lower = faster RT offset)
        "baseline_speed": rng.normal(loc=0.0, scale=1.0, size=N_SUBJ)
    })

    rows = []
    for _, s in subjects.iterrows():
        # random subject intercept (ms)
        subj_offset = rng.normal(0, 80)  # between-person variability
        # accuracy tendency (fast-but-error-prone archetype)
        err_bias = rng.normal(0, 0.05)
        for cond in CONDITIONS:
            for t in range(N_TRIALS_PER_COND):
                # base RTs: congruent faster than incongruent
                base = 550 if cond == "congruent" else 650
                # trial noise
                noise = rng.normal(0, 120)
                # baseline_speed: faster people shave time, slower add time
                rt = base + subj_offset - 25*s["baseline_speed"] + noise

                # accuracy: a bit worse for incongruent
                p_correct = 0.97 if cond == "congruent" else 0.90
                p_correct += -0.03*max(0, s["baseline_speed"]) + err_bias
                p_correct = np.clip(p_correct, 0.75, 0.99)
                correct = rng.random() < p_correct

                # sprinkle outliers (anticipations & lapses)
                if rng.random() < 0.03:
                    rt = rng.normal(150, 30)   # anticipatory
                if rng.random() < 0.04:
                    rt = rng.normal(2300, 200) # lapse

                rt = max(80, rt)  # keep sane

                rows.append({
                    "subject": int(s["subject"]),
                    "condition": cond,
                    "trial": t+1,
                    "rt_ms": float(rt),
                    "correct": int(correct),
                })

    trials = pd.DataFrame(rows)
    subjects.to_csv("data/synthetic/psych_stroop_subjects.csv", index=False)
    trials.to_csv("data/synthetic/psych_stroop_trials.csv", index=False)
    print("Wrote data/synthetic/psych_stroop_subjects.csv and psych_stroop_trials.csv")

if __name__ == "__main__":
    simulate()
