# SPDX-License-Identifier: MIT
"""
Simulate trial-level Stroop data (plausible undergrad study).
Creates in --outdir (default: data/synthetic):
  psych_stroop_trials.csv
  psych_stroop_subjects.csv
  psych_stroop_meta.json
"""

import argparse
import json
import time
import pathlib
from pathlib import Path

import numpy as np
import pandas as pd

# Defaults (kept explicit so meta stays in sync)
RNG_SEED_DEFAULT = 42
N_SUBJ_DEFAULT = 60
N_TRIALS_PER_COND_DEFAULT = 100
CONDITIONS = ["congruent", "incongruent"]

# Parameters
BASE_RT_CONGRUENT = 550       # ms
BASE_RT_INCONGRUENT = 650     # ms (=> 100 ms penalty)
BETWEEN_PERSON_RT_SD = 80     # ms subject intercept variation
TRIAL_NOISE_SD = 120          # ms trial-to-trial noise
BASELINE_SPEED_EFFECT = 25    # ms per +1 SD baseline_speed (faster -> shave time)

ACC_BASE_CONGRUENT = 0.97
ACC_BASE_INCONGRUENT = 0.90   # (=> 0.07 penalty)
ACC_BSL_SPEED_PENALTY = 0.03  # subtract per +1 SD if positive
ACC_ERR_BIAS_SD = 0.05
ACC_CLIP = (0.75, 0.99)

OUTLIER_RATE_ANTICIP = 0.03
OUTLIER_RT_ANTICIP_MU = 150
OUTLIER_RT_ANTICIP_SD = 30
OUTLIER_RATE_LAPSE = 0.04
OUTLIER_RT_LAPSE_MU = 2300
OUTLIER_RT_LAPSE_SD = 200
RT_FLOOR = 80


def simulate(
    n_subjects: int = N_SUBJ_DEFAULT,
    n_trials: int = N_TRIALS_PER_COND_DEFAULT,
    seed: int = RNG_SEED_DEFAULT,
    outdir: Path = Path("data/synthetic"),
):
    """Simulates Stroop data and writes CSVs to outdir."""
    rng = np.random.default_rng(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    # subject-level covariates
    subjects = pd.DataFrame(
        {
            "subject": np.arange(1, n_subjects + 1),
            "gender": rng.choice(["F", "M"], size=n_subjects, p=[0.6, 0.4]),
            "handedness": rng.choice(["R", "L"], size=n_subjects, p=[0.9, 0.1]),
            # baseline processing speed (lower = faster RT offset)
            "baseline_speed": rng.normal(loc=0.0, scale=1.0, size=n_subjects),
        }
    )

    rows = []
    for _, s in subjects.iterrows():
        # random subject intercept (ms)
        subj_offset = rng.normal(0, BETWEEN_PERSON_RT_SD)
        # accuracy tendency (fast-but-error-prone archetype)
        err_bias = rng.normal(0, ACC_ERR_BIAS_SD)

        for cond in CONDITIONS:
            for t in range(n_trials):
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
                    rt = rng.normal(OUTLIER_RT_ANTICIP_MU, OUTLIER_RT_ANTICIP_SD)  # anticipatory
                if rng.random() < OUTLIER_RATE_LAPSE:
                    rt = rng.normal(OUTLIER_RT_LAPSE_MU, OUTLIER_RT_LAPSE_SD)  # lapse

                rt = max(RT_FLOOR, float(rt))  # keep sane

                rows.append(
                    {
                        "subject": int(s["subject"]),
                        "condition": cond,
                        "trial": int(t + 1),
                        "rt_ms": rt,
                        "correct": int(correct),
                    }
                )

    trials = pd.DataFrame(rows)

    # write CSVs
    subjects_path = outdir / "psych_stroop_subjects.csv"
    trials_path = outdir / "psych_stroop_trials.csv"
    subjects.to_csv(subjects_path, index=False)
    trials.to_csv(trials_path, index=False)
    print(f"Wrote {subjects_path} and {trials_path}")

    # Write meta *after* simulation is done
    write_meta(
        subjects=subjects,
        trials=trials,
        outdir=outdir,
        seed=seed,
        n_trials_per_cond=n_trials,
    )

    return subjects, trials


def write_meta(
    subjects: pd.DataFrame,
    trials: pd.DataFrame,
    outdir: Path,
    seed: int,
    n_trials_per_cond: int,
):
    meta = dict(
        seed=seed,
        n_subjects=int(len(subjects)),
        n_trials_per_cond=int(n_trials_per_cond),
        conditions=CONDITIONS,
        rt_ms=dict(
            base_congruent=BASE_RT_CONGRUENT,
            base_incongruent=BASE_RT_INCONGRUENT,
            incongruent_penalty=BASE_RT_INCONGRUENT - BASE_RT_CONGRUENT,
            between_person_sd=BETWEEN_PERSON_RT_SD,
            trial_noise_sd=TRIAL_NOISE_SD,
            baseline_speed_effect_ms_per_sd=BASELINE_SPEED_EFFECT,
            outliers=dict(
                anticipations=dict(
                    rate=OUTLIER_RATE_ANTICIP, mu=OUTLIER_RT_ANTICIP_MU, sd=OUTLIER_RT_ANTICIP_SD
                ),
                lapses=dict(
                    rate=OUTLIER_RATE_LAPSE, mu=OUTLIER_RT_LAPSE_MU, sd=OUTLIER_RT_LAPSE_SD
                ),
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
        file_rows=dict(subjects=int(len(subjects)), trials=int(len(trials))),
    )
    meta_path = outdir / "psych_stroop_meta.json"
    with meta_path.open("w") as f:
        json.dump(meta, f, indent=2)
    print(f"Wrote {meta_path}")


def main():
    ap = argparse.ArgumentParser(description="Simulate trial-level Stroop data")
    ap.add_argument("--seed", type=int, default=RNG_SEED_DEFAULT)
    ap.add_argument("--n-subjects", type=int, default=N_SUBJ_DEFAULT)
    ap.add_argument("--n-trials", type=int, default=N_TRIALS_PER_COND_DEFAULT)
    ap.add_argument(
        "--outdir",
        type=pathlib.Path,
        default=Path("data/synthetic"),
        help="Where to write outputs (CSV/JSON).",
    )
    args = ap.parse_args()

    simulate(
        n_subjects=args.n_subjects,
        n_trials=args.n_trials,
        seed=args.seed,
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
