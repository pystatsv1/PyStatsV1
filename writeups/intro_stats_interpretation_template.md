# Intro Stats Case Study — Interpretation Template

Use this short template after you run the Intro Stats case study pack.

> **Tip:** Keep it simple. Your goal is to communicate what you did and what it means.

## 1) Research question

In one sentence:

- **Question:** Do students in the **treatment** group score higher than students in the **control** group?

## 2) Variables

- **Outcome (numeric):** `score` (final exam score)
- **Group (categorical):** `group` (`control`, `treatment`)

## 3) Descriptives

From `outputs/case_studies/intro_stats/group_summary.csv`:

- Control mean (SD): ________
- Treatment mean (SD): ________
- Mean difference (treatment − control): ________

## 4) Distributions and outliers

From `outputs/case_studies/intro_stats/score_distributions.png`:

- Are the distributions roughly similar shape?
- Any obvious outliers? (If yes, note them and how you handled them.)

Notes:

- ______________________________________________________________________
- ______________________________________________________________________

## 5) Confidence intervals

From `outputs/case_studies/intro_stats/ci_mean_diff_welch_95.csv`:

- 95% CI for the mean difference: [ ________, ________ ]

Interpretation (in words):

- ______________________________________________________________________

## 6) Hypothesis test by simulation

From `outputs/case_studies/intro_stats/permutation_test_summary.csv`:

- Two-sided permutation p-value: ________

Interpretation:

- If the p-value is small, the observed difference would be **rare** under “no group effect”.
- If the p-value is not small, the observed difference could be explained by random group assignment.

## 7) Effect size

From `outputs/case_studies/intro_stats/effect_size.csv`:

- Cohen’s d: ________
- (Optional) Hedges’ g: ________

Interpretation (rough guide):

- ~0.2 small, ~0.5 medium, ~0.8 large (very rough — context matters)

## 8) Conclusion

Write 2–4 sentences:

- What did you find?
- How confident are you?
- What would you do next (more data, better study design, different outcome, etc.)?

Conclusion:

- ______________________________________________________________________
- ______________________________________________________________________
- ______________________________________________________________________
