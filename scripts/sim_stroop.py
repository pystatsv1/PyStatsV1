import argparse
# SPDX-License-Identifier: MIT
"""
Simulate trial-level Stroop data (plausible undergrad study).
Creates:
  data/synthetic/psych_stroop_trials.csv
  data/synthetic/psych_stroop_subjects.csv
  data/synthetic/psych_stroop_meta.json
"""
import os, time, json
import numpy as np
import pandas as pd

RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

N_SUBJ = 60
N_TRIALS_PER_COND = 100
CONDITIONS = ["congruent", "incongruent"]

# Parameters (kept explicit so meta stays in sync)
BASE_RT_CONGRUENT = 550      # ms
BASE_RT_INCONGRUENT = 650    # ms (=> 100 ms penalty)
BETWEEN_PERSON_RT_SD = 80    # ms subject intercept variation
TRIAL_NOISE_SD = 120         # ms trial-to-trial noise
BASELINE_SPEED_EFFECT = 25   # ms per +1 SD baseline_speed (faster -> shave time)
ACC_BASE_CONGRUENT = 0.97
ACC_BASE_INCONGRUENT = 0.90  # (=> 0.07 penalty)
ACC_BSL_SPEED_PENALTY = 0.03 # subtract per +1 SD if positive
ACC_ERR_BIAS_SD = 0.05
ACC_CLIP = (0.75, 0.99)
OUTLIER_RATE_ANTICIP = 0.03
OUTLIER_RT_ANTICIP_MU = 150
OUTLIER_RT_ANTICIP_SD = 30
OUTLIER_RATE_LAPSE = 0.04
OUTLIER_RT_LAPSE_MU = 2300
OUTLIER_RT_LAPSE_SD = 200
RT_FLOOR = 80

def simulate():
    os.makedirs("data/synthetic", exist_ok=True)

    # subject-level covariates
    subjects = pd.DataFrame({
        "subject": np.arange(1, N_SUBJ + 1),
        "gender": rng.choice(["F", "M"], size=N_SUBJ, p=[0.6, 0.4]),
        "handedness": rng.choice(["R", "L"], size=N_SUBJ, p=[0.9, 0.1]),
        # baseline processing speed (lower = faster RT offset)
        "baseline_speed": rng.normal(loc=0.0, scale=1.0, size=N_SUBJ)
    })

    rows = []
    for _, s in subjects.iterrows():
        # random subject intercept (ms)
        subj_offset = rng.normal(0, BETWEEN_PERSON_RT_SD)  # between-person variability
        # accuracy tendency (fast-but-error-prone archetype)
        err_bias = rng.normal(0, ACC_ERR_BIAS_SD)

        for cond in CONDITIONS:
            for t in range(N_TRIALS_PER_COND):
                # base RTs
                base = BASE_RT_CONGRUENT if cond == "congruent" else BASE_RT_INCONGRUENT
                # trial noise
                noise = rng.normal(0, TRIAL_NOISE_SD)
                # baseline_speed: faster people shave time, slower add time
                rt = base + subj_offset - BASELINE_SPEED_EFFECT * s["baseline_speed"] + noise

                # accuracy: a bit worse for incongruent
                p_correct = ACC_BASE_CONGRUENT if cond == "congruent" else ACC_BASE_INCONGRUENT
                p_correct += -ACC_BSL_SPEED_PENALTY * max(0, s["baseline_speed"]) + err_bias
                p_correct = float(np.clip(p_correct, *ACC_CLIP))
                correct = bool(rng.random() < p_correct)

                # sprinkle outliers (anticipations & lapses)
                if rng.random() < OUTLIER_RATE_ANTICIP:
                    rt = rng.normal(OUTLIER_RT_ANTICIP_MU, OUTLIER_RT_ANTICIP_SD)    # anticipatory
                if rng.random() < OUTLIER_RATE_LAPSE:
                    rt = rng.normal(OUTLIER_RT_LAPSE_MU, OUTLIER_RT_LAPSE_SD)      # lapse

                rt = max(RT_FLOOR, float(rt))  # keep sane

                rows.append({
                    "subject": int(s["subject"]),
                    "condition": cond,
                    "trial": int(t + 1),
                    "rt_ms": rt,
                    "correct": int(correct),
                })

    trials = pd.DataFrame(rows)

    # write CSVs
    subjects.to_csv("data/synthetic/psych_stroop_subjects.csv", index=False)
    trials.to_csv("data/synthetic/psych_stroop_trials.csv", index=False)
    print("Wrote data/synthetic/psych_stroop_subjects.csv and psych_stroop_trials.csv")

    return subjects, trials

def write_meta(subjects: pd.DataFrame, trials: pd.DataFrame):
    meta = dict(
        seed=RNG_SEED,
        n_subjects=int(len(subjects)),
        n_trials_per_cond=int(N_TRIALS_PER_COND),
        conditions=CONDITIONS,
        rt_ms=dict(
            base_congruent=BASE_RT_CONGRUENT,
            base_incongruent=BASE_RT_INCONGRUENT,
            incongruent_penalty=BASE_RT_INCONGRUENT - BASE_RT_CONGRUENT,
            between_person_sd=BETWEEN_PERSON_RT_SD,
            trial_noise_sd=TRIAL_NOISE_SD,
            baseline_speed_effect_ms_per_sd=BASELINE_SPEED_EFFECT,
            outliers=dict(
                anticipations=dict(rate=OUTLIER_RATE_ANTICIP,
                                   mu=OUTLIER_RT_ANTICIP_MU, sd=OUTLIER_RT_ANTICIP_SD),
                lapses=dict(rate=OUTLIER_RATE_LAPSE,
                            mu=OUTLIER_RT_LAPSE_MU, sd=OUTLIER_RT_LAPSE_SD),
            ),
            floor_ms=RT_FLOOR,
        ),
        acc=dict(
            base_congruent=ACC_BASE_CONGRUENT,
            base_incongruent=ACC_BASE_INCONGRUENT,
            incongruent_penalty=ACC_BASE_CONGRUENT - ACC_BASE_INCONGRUENT,
            baseline_speed_penalty_per_sd=ACC_BSL_SPEED_PENALTY,
            error_bias_sd=ACC_ERR_BIAS_SD,
            clip=list(ACC_CLIP),
        ),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        file_rows=dict(
            subjects=int(len(subjects)),
            trials=int(len(trials)),
        ),
    )
    with open("data/synthetic/psych_stroop_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Wrote data/synthetic/psych_stroop_meta.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-subjects", type=int, default=60)
    ap.add_argument("--n-trials", type=int, default=100)
    args = ap.parse_args()
    global N_SUBJ, N_TRIALS_PER_COND, rng, RNG_SEED
    N_SUBJ = args.n_subjects
    N_TRIALS_PER_COND = args.n_trials
    RNG_SEED = args.seed
    rng = np.random.default_rng(RNG_SEED)
    subjects_df, trials_df = simulate()
    write_meta(subjects_df, trials_df)

if __name__ == "__main__":
    main()