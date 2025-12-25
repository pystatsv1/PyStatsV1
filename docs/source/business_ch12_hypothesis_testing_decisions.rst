Chapter 12 — Hypothesis Testing for Decisions (Practical, Not Math-Heavy)
======================================================================

Accountants are constantly asked versions of:

- "Did the ad work?"
- "Did the new AP tool actually make us faster?"
- "Is this improvement real — or just random noise?"

This chapter reframes hypothesis testing as **business experimentation**.
Instead of starting from formulas, we start from **decisions** and the way
those decisions are justified in real organizations.

Learning objectives
-------------------

By the end of this chapter, you should be able to:

1. **Frame business questions as testable hypotheses.**
   Example: "Average order value didn't change" becomes a *null hypothesis*.

2. **Interpret p-values and effect sizes together.**
   A p-value answers: *"Is the effect unlikely under the null?"*
   Effect size answers: *"If real, does it matter to the business?"*

3. **Avoid "significant but irrelevant" outcomes.**
   A tiny, statistically significant improvement can still be a bad decision
   if it costs more to measure or implement than it saves.

4. **Write a pre-commitment plan (anti p-hacking).**
   Decide the metric, test, confidence level, and stopping rule *before* you
   look at results.

What this chapter produces
--------------------------

Running the chapter script writes deterministic artifacts into
``outputs/track_d``:

- ``ch12_experiment_design.json`` — pre-commitment plan
- ``ch12_hypothesis_testing_summary.json`` — results (p-values + effect sizes)
- ``ch12_decision_memo.md`` — an executive memo (10 bullets)
- ``figures/`` + ``ch12_figures_manifest.csv`` — charts + metadata

We keep the artifacts *audit-friendly*: clear assumptions, a traceable seed,
and an explicit separation between **statistical significance** and **business
significance**.

Two worked examples (teaching cases)
------------------------------------

Because NSO v1 is a compact synthetic dataset without explicit regions or
promotion flags, we construct two **deterministic teaching cases** from the
input data:

1. **Promotion test (A/B test style)**

   - *Question:* Did a promotion increase AOV (average order value)?
   - *Null hypothesis:* Promo AOV = Control AOV.
   - *Approach:*

     - Assign customers into "promo" vs "control" groups deterministically.
     - Choose a promo month (the month with the most invoices).
     - Use a permutation test for the mean difference (robust and simple).
     - Report p-value + mean difference + a bootstrap confidence interval.

2. **Cycle-time analysis (before/after)**

   - *Question:* Did the new AP workflow reduce invoice processing cycle time?
   - *Null hypothesis:* Mean days-to-pay is the same before and after.
   - *Approach:*

     - Compute days between AP invoice and AP payment.
     - Split invoices into "before" and "after" based on invoice date.
     - Use a permutation test for the mean difference.
     - Report p-value + mean reduction in days + a bootstrap confidence interval.

Decision language (the point of the chapter)
-------------------------------------------

A good hypothesis test report translates results into an operational decision:

- "We saw a **~$X increase in AOV**, with a p-value of **p**."
- "We saw a **~Y day reduction** in AP cycle time, with a p-value of **p**."

But it also states limits clearly:

- Sample size
- Confidence level
- Practical thresholds (materiality)
- The risks of multiple testing / early stopping

End-of-chapter problems (from the vision)
-----------------------------------------

1. **The Promotion Test**

   Analyze sales data from two regions (one with a promo, one without). Did the
   promo region actually outperform the control group after accounting for
   natural variance?

2. **Cycle Time Analysis**

   The AP team changed their software. Compare "Days to Process Invoice" before
   and after. Is the reduction statistically significant, or just random noise?

3. **P-Hacking Prevention**

   Identify common ways teams "cheat" to get a result (multiple metrics, early
   stopping, slicing timeframes). Propose a pre-commitment rule to prevent this.

How to run
----------

From the repo root:

.. code-block:: bash

   make business-ch12

