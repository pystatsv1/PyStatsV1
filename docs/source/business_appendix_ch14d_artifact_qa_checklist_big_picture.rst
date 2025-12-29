Appendix 14D: Artifact QA checklist (big picture — what and why before you share results)
========================================================================================

Chapter 14 produces an “analysis pack” of outputs: a driver table, a short memo, model summaries,
and figures. These artifacts are designed to be reproducible and explainable.

But “explainable” does not automatically mean “safe to share.”

This appendix is a **professional QA checklist** for accountants and analysts — the “what and why”
you should verify before you:

- send the memo to leadership,
- paste coefficients into a forecast model,
- brief operations on “what drives COGS,” or
- publish results in a report.

The goal is not perfection. The goal is **trustworthy communication**:
your results should be accurate, traceable, and framed with the right guardrails.

What QA protects you from
-------------------------

In real accounting/FP&A work, the biggest failure modes are rarely “math errors.”
They tend to be:

- **Measurement errors** (wrong sign, wrong month, wrong definition)
- **Broken lineage** (numbers cannot be traced back to a credible source)
- **Over-interpretation** (treating a driver lens as causation)
- **Model fragility** (one month or one event dominates the fit)
- **Reporting drift** (figures and memo say different things)
- **Reproducibility gaps** (nobody can recreate what you did next week)

Chapter 14 exists to teach a regression workflow that behaves like accounting work:
disciplined, auditable, and fit for planning conversations.

This QA checklist is the “controls layer” on top of the analysis pack.

Inputs and outputs in scope
---------------------------

This checklist assumes the standard Chapter 14 artifacts:

- ``ch14_driver_table.csv``
- ``ch14_regression_memo.md``
- ``ch14_regression_summary.json``
- ``ch14_regression_design.json``
- ``ch14_figures_manifest.csv``
- ``figures/`` (PNG charts referenced by the manifest)

and that the dataset (NSO v1) exists locally under:

- ``data/synthetic/nso_v1/``

Quick start: the 5-minute QA pass
---------------------------------

If you only have five minutes, do these checks in this order:

1) Open ``ch14_driver_table.csv`` and confirm months are complete and sorted.

2) Confirm sign conventions:
   - ``units_sold`` should be positive (for the Chapter 14 driver table definition).

3) Read ``ch14_regression_memo.md`` and check the “story” matches your intuition:
   - baseline vs rate interpretation
   - driver lens, not causation

4) Open the figures listed in ``ch14_figures_manifest.csv``:
   - does the relationship look reasonably linear?
   - any obvious outlier month dominating?

5) Confirm all expected artifacts exist (no missing files) and rerun:

   .. code-block:: bash

      make business-ch14

If anything looks off in the 5-minute pass, stop and do the deeper pass below.

Deeper QA: the 30-minute professional pass
------------------------------------------

This section is organized as a set of gates. You do not need to “check everything forever.”
You are trying to reach a reasonable professional standard before sharing results.

Gate 1 — Provenance and reproducibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** if you can’t recreate the results, you can’t defend them.

Checks:

- Record (or confirm) the dataset and run command used.
  In this project, the most common baseline run is:

  .. code-block:: bash

     make business-nso-sim
     make business-validate
     make business-ch14

- Confirm that artifacts are generated (not manually edited).
  The outputs live under:

  - ``outputs/track_d/track_d/``

- Confirm you can regenerate cleanly and get the same results (same dataset + seed).

Red flags:

- You cannot identify which dataset folder was used.
- A teammate cannot reproduce your numbers on the same commit.

Gate 2 — Driver table integrity (the foundation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** regression can look “precise” even when the inputs are wrong.
The driver table is the “data contract” of Chapter 14.

Open: ``ch14_driver_table.csv``

Checks:

- **Month coverage**
  - Are months continuous (no unexpected gaps)?
  - Is the time window what you expect (e.g., last 12/24 months)?

- **Sorting and duplicates**
  - One row per month.
  - No duplicated months.
  - Months are in chronological order.

- **Sign conventions**
  - ``units_sold`` is positive (per Chapter 14 definition).
  - Revenue and COGS have the expected sign convention for your statements.

- **Magnitude sanity**
  - Units, revenue, and COGS are in plausible ranges.
  - No single month is wildly out of scale unless the business story explains it.

- **Lineage plausibility**
  - Units sold came from inventory movements.
  - Invoice count came from A/R events.
  - Revenue and COGS came from monthly income statement lines.

Common errors this catches:

- Units sold computed with the wrong sign
- Mismatched month keys (e.g., revenue in one month, units in another)
- Missing months due to filtering
- “Accidental duplicates” caused by grouping logic

Gate 3 — Model sanity (baseline vs rate)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** accountants often use regression to separate “fixed vs variable”
or to build planning rates. If slopes/intercepts are not plausible, your plan will be wrong.

Open: ``ch14_regression_summary.json`` and/or read ``ch14_regression_memo.md``

Checks:

- **Direction makes sense**
  - Revenue slope vs units should be positive.
  - COGS slope vs units should be positive.
  - If a slope is negative, treat it as a stop sign until explained.

- **Intercept (baseline) plausibility**
  - For revenue: a large positive intercept may indicate timing or non-unit revenue.
  - For COGS: a positive intercept might reflect baseline costs, but it should be explainable.

- **Rate plausibility**
  - Revenue-per-unit lens: does it roughly match a blended selling price you’d believe?
  - COGS-per-unit lens: does it roughly match a blended unit cost you’d believe?

- **R² interpretation discipline**
  - R² is not “truth”; it’s “how much of the variance the model explains in-sample.”
  - High R² may also reflect seasonality/timing; it does not prove causation.

Common errors this catches:

- A driver computed incorrectly yields implausible slopes
- A single outlier month inflates or distorts fit
- A mismatch between “what the memo claims” and the actual coefficients

Gate 4 — Outliers and dominance (is one month driving everything?)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** a fit can look good but be driven by one extreme point.
That’s dangerous for planning.

Checks:

- Open the figures referenced by ``ch14_figures_manifest.csv`` and look for:
  - a single month far from the rest,
  - a fitted line that “aims” mainly at one point,
  - clusters that suggest regime changes (early months behave differently than later months).

- Optional: do a “remove-one-month” thought experiment:
  - If one month is extreme, ask: would the slope change drastically if that month disappeared?

Interpretation outcome:

- If one point dominates, you can still share the analysis — but you must say:
  “Results are sensitive to month X; treat slopes as tentative.”

Gate 5 — Residual pattern check (is the driver lens stable?)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** patterned residuals often indicate missing drivers, mix shifts, or nonlinearity.

Checks:

- Look for systematic patterns in the “actual vs predicted” style figure(s):
  - consecutive months consistently above/below prediction,
  - seasonal shape not captured by the model,
  - “break point” behavior (model works then stops working).

How to respond professionally:

- If residuals look random-ish, your driver lens is likely stable enough for planning.
- If residuals show patterns, share results with explicit caveats:
  “This suggests mix shifts/seasonality; consider segmentation or seasonality indicators.”

Gate 6 — Artifact completeness and internal consistency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** leadership will ask “where did that number come from?”
You want your artifacts to agree with each other.

Checks:

- All expected files exist in the outputs folder.
- ``ch14_figures_manifest.csv`` lists figure files that actually exist under ``figures/``.
- The memo’s described slopes/baseline story matches the JSON summary.
- The “design contract” matches the chapter narrative (models m1/m2/m3 as documented).

This is where you catch subtle errors like:

- The code changed but the memo language wasn’t updated
- Figures were generated from an older run
- A refactor changed output paths

Gate 7 — Communication guardrails (what you are allowed to claim)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why this matters:** the most common professional failure is claiming causation or certainty.

Before you share the memo, confirm it clearly communicates:

- Regression here is a **driver lens**, not causation proof.
- Slopes are **planning rates**, not immutable laws.
- Structural changes (pricing, mix, capacity, policy) can break the relationship.
- Residuals represent “unexplained movement” that may require investigation.

A safe, professional phrasing pattern is:

- “Given the recent history in this dataset, the implied rate is…”
- “If units move by X, the model implies outcome moves by about Y, subject to residual variation.”
- “This month is an outlier relative to the driver story; investigate…”
- “This is useful for planning; not evidence of causality.”

Sharing checklist (go / no-go)
------------------------------

**Go** when:

- Driver table looks correct and complete.
- Slopes and intercepts are plausible and interpretable.
- Figures do not show a single point dominating the fit.
- Residuals do not show severe patterns (or patterns are clearly caveated).
- Memo matches JSON results and includes guardrails.

**No-go (pause and fix)** when:

- Units sold has the wrong sign or months are missing/duplicated.
- Slopes have implausible direction or magnitude without explanation.
- A single month dominates and the memo does not warn about sensitivity.
- Artifacts are missing or inconsistent (manifest vs files, memo vs JSON).

Closing note: QA is part of the method, not a separate chore
------------------------------------------------------------

In Track D, the method is not just “run regression.”
The method is:

- measurement discipline,
- reproducible artifacts,
- explainable coefficients,
- and professional communication guardrails.

Appendix 14C tells you what each artifact is.
Appendix 14D tells you how to **trust and communicate** those artifacts responsibly.
