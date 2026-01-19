Chapter 13 — Correlation, Causation, and Controlled Comparisons
===============================================================

.. |trackd_run| replace:: d13
.. include:: _includes/track_d_run_strip.rst


This chapter is about **not fooling yourself** (or your stakeholders) when you see two lines move together.

Accountants are trained to explain variances. The trap is when a tidy story turns into a causal claim:
“X increased, so X *caused* Y.” Often, **a third factor** (seasonality, activity level, headcount) moves both.

What you’ll build in this chapter
---------------------------------

Using the North Shore Outfitters (NSO) running case, you’ll produce a small “correlation audit” pack:

* A **naïve correlation** (two variables move together).
* A **controlled comparison** (same correlation after “controlling for” a third variable).
* A short **executive memo** explaining what you can and cannot claim.

Key terms (accounting ↔ data)
-----------------------------

**Correlation (r)**
    A number from -1 to +1 that measures linear co-movement. It is not proof of cause.

**Causation**
    A claim that changing X would change Y (a “do” statement). Requires design, not vibes.

**Confounder / third variable**
    A variable Z that influences both X and Y, creating a misleading relationship.

**Control variable**
    The variable(s) you hold constant (or adjust for) to isolate a relationship of interest.

**Partial correlation (controlled correlation)**
    Correlation between X and Y *after removing the linear effect of Z* from both.

Running case inputs
-------------------

The script reads NSO v1 synthetic outputs (created earlier in Track D), especially:

* ``gl_journal.csv`` — transaction-level general ledger entries.
* ``statements_is_monthly.csv`` — income statement summaries (used for sanity checks).

Outputs
-------

When you run the Chapter 13 script, it writes:

* ``ch13_controlled_comparisons_design.json`` — pre-committed variables + controls.
* ``ch13_correlation_summary.json`` — correlations, partial correlations, and notes.
* ``ch13_correlation_memo.md`` — a CFO-style memo (what we know / don’t know).
* ``figures/`` + ``ch13_figures_manifest.csv`` — plots and a manifest for docs/RTD.

How to run
----------

From the repo root:

.. code-block:: bash

   make business-ch13

Or directly:

.. code-block:: bash

   python -m scripts.business_ch13_correlation_causation_controlled_comparisons \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

How to interpret the results (what “good” looks like)
-----------------------------------------------------

1. **Naïve correlation is a prompt, not an answer.**
   It tells you “look here,” not “this caused that.”

2. **Controlled comparisons shrink bad stories.**
   If Revenue correlates with Payroll Taxes, the real driver may be Payroll Expense.
   Partial correlation helps you say: “The Revenue–PayrollTax link mostly disappears once we control for Payroll.”

3. **Write the correct sentence.**
   *Bad:* “Revenue causes payroll taxes.”
   *Better:* “Revenue and payroll taxes move together, but payroll explains most of that relationship.
   A causal claim would require a designed change (e.g., staffing policy) and a comparison group.”

End-of-chapter problems
-----------------------

1. **Confounding variable**
   Find two NSO metrics that move together and propose a plausible third variable that drives both.
   Write the “wrong” story and then correct it.

2. **Narrative correction**
   Rewrite an overconfident causal statement into a defensible statement that acknowledges confounding.

3. **Controlled comparison**
   Pick a control variable and recompute the relationship (partial correlation).
   Explain why the control is reasonable in accounting terms.
