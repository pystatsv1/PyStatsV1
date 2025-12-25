Chapter 12 — Hypothesis Testing for Decisions 
=======================================================================

Why this chapter exists
-----------------------
Most teams *think* they are making data-driven decisions, but often they are really
reacting to random noise:

- “Sales were higher this week — the promo worked!”
- “Cycle time dropped — the new process is better!”

This chapter reframes hypothesis testing as **business experimentation**: a disciplined
way to decide whether a change is likely *real* and whether it is **worth acting on**.

What “good” looks like in this book
-----------------------------------
Clean books → reliable dataset → defensible analysis → usable forecast → decision memo

Chapter 12 focuses on the **decision memo** step:

- Did we measure the right thing?
- Did we pre-commit to the metric and the test window?
- Is the effect big enough to matter (not just “statistically significant”)?

Key accounting & operations terms (quick definitions)
-----------------------------------------------------
Accounts Receivable (AR)
   Money customers owe you. In the NSO case, AR invoices and collections are recorded as events.

Accounts Payable (AP)
   Money you owe suppliers. In NSO, AP invoices and payments are recorded as events.

Invoice
   A request for payment tied to a sale (AR) or a supplier bill (AP). In this project, invoices are identified by ``invoice_id``.

Average Order Value (AOV)
   Average invoice amount (here, for AR invoices). Used as the “promotion” outcome metric.

Cycle Time (AP processing)
   Time between an AP invoice date and payment date. Here we approximate **days-to-pay**.

Control vs Treatment
   Two groups: “business as usual” (control) vs “new thing” (treatment).

Null Hypothesis (H0)
   “No difference” (promo has no effect; new AP process saves no time).

Alternative Hypothesis (H1)
   “There is a difference” (promo changes AOV; process reduces cycle time).

P-value
   Under H0 (“no effect”), how surprising is what we observed? Small p-values mean the result is
   unlikely *if there truly were no effect*.

Alpha (decision threshold)
   The rule you set **before** looking at results (commonly 0.05). In this repo we tie alpha to the confidence level.

Effect Size
   “How big is the impact?” Example: dollars per invoice, or days saved per invoice.

Practical (business) significance
   “Even if real, is it worth doing?” A statistically real effect can still be too small to matter.

P-hacking
   Accidental or intentional “cheating” (testing many metrics, peeking early, changing rules after seeing results)
   until something looks significant.

What the software does (two deterministic teaching cases)
---------------------------------------------------------
NSO v1 doesn’t contain explicit region/promo labels, so we create two **deterministic teaching cases**
from NSO’s event tables:

1) Promotion test (A/B style)
   - Customers are deterministically assigned to **treatment** or **control**
   - We choose a promo month with many invoices (stable sample size)
   - We apply a small, configurable uplift to treatment invoices (teaching knob)
   - We estimate a p-value using a **permutation test** on mean invoice amount
   - We report effect size + bootstrap confidence interval (CI)

2) Cycle time test (before/after)
   - We compute AP days-to-pay using invoice + payment dates
   - We split invoices into **before** vs **after** around a changeover date
   - We apply a small, configurable cycle-time reduction to the after group (teaching knob)
   - We test (before − after) mean difference with the same permutation discipline

Running Chapter 12
------------------
From the repo root:

.. code-block:: bash

   make business-ch12

Or directly:

.. code-block:: bash

   python -m scripts.business_ch12_hypothesis_testing_decisions \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs (what to read first)
----------------------------
The script writes artifacts into ``outputs/track_d``:

- ``ch12_experiment_design.json``
  Pre-commitment file (anti p-hacking): metric, alpha, and decision rule.

- ``ch12_hypothesis_testing_summary.json``
  Machine-readable summary: p-values, effect sizes, CIs.

- ``ch12_experiment_memo.md``
  Executive-style memo: “what happened, what it means, what to do.”

- ``ch12_figures_manifest.csv`` + charts in ``outputs/track_d/figures/``
  Charts follow the repo’s style contract and include guardrails to avoid misleading visuals.

How to interpret the results (accountant-friendly)
--------------------------------------------------
Promotion test (AR invoices)
   Ask two questions:

   1) Is it likely real?
      - p < alpha suggests the observed lift is unlikely under “no effect.”

   2) Is it worth it?
      - Compare the estimated lift (dollars per invoice and % lift) to the cost of the promo
        and to margin impact (a 2% revenue lift can be negative value if discounts overwhelm margin).

Cycle time test (AP days-to-pay)
   Translate days saved into dollars:

   - Labor time saved (processing effort)
   - Early-pay discounts captured
   - Fewer late fees / fewer supplier escalations
   - Stronger cash planning (predictable AP timing)

Guardrails (what we do *not* allow)
-----------------------------------
- Do not “peek” and stop the test early.
- Do not change the metric after seeing results.
- Do not test 20 metrics and celebrate the one that passes.
- Always pair p-values with effect size + CI.

End-of-chapter problems (use our outputs)
-----------------------------------------
1) Promotion test decision memo
   Using ``ch12_hypothesis_testing_summary.json`` and the memo template style:
   - State H0 and H1 in business language
   - Report p-value, effect size, and CI
   - Define a “minimum practical lift” and decide rollout / no-rollout

2) Process change evaluation
   Using the cycle-time results:
   - Convert days saved into approximate annual dollars
   - Decide whether benefits exceed implementation costs

3) P-hacking prevention
   List five ways teams accidentally p-hack, and write a pre-commitment rule set that would prevent each one.
