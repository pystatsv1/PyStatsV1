Track D — Chapter 9: Visualization and reporting that doesn’t mislead
=====================================================================

.. |trackd_run| replace:: d09
.. include:: _includes/track_d_run_strip.rst

Chapter 9 introduces a conservative **plotting + reporting style contract** for Track D.
The point is not to make beautiful charts — it is to make charts that are
**hard to misread** and **hard to misuse**.

In business settings, a chart is often treated as “proof.” This chapter teaches
how to match the **intent** of a chart to its **design**, and how to add small
guardrails so the visuals remain honest.

Learning objectives
-------------------

By the end of Chapter 9, you should be able to:

- **Choose the right chart** for the question (trend vs. comparison vs. distribution).
- **Avoid common visualization pitfalls** (“chart crimes”) such as y-axis truncation,
  cherry-picked time windows, and ambiguous labels.
- **Produce a one-page executive story**: a compact narrative that summarizes the key
  insights from a small chart pack (strictly limited to 10 bullets).

What we implement in code
-------------------------

This chapter implements two things:

1) A reusable style/guardrails module:

- ``scripts/_reporting_style.py``

2) A Chapter 9 driver that produces a small, compliant “chart pack” + manifest:

- ``scripts/business_ch09_reporting_style_contract.py``

The style contract (rules)
--------------------------

The style contract lives in ``scripts/_reporting_style.py`` as ``STYLE_CONTRACT``.
It is intentionally conservative so later chapters can reuse it.

Allowed chart types
^^^^^^^^^^^^^^^^^^^

- **Line**: trends over time (monthly KPIs, DSO).
- **Bar**: categorical comparisons (by product, by department) *with a zero baseline*.
- **Histogram**: distribution shape.
- **ECDF**: distribution tails (what fraction is below a threshold?).
- **Box**: distribution comparison across groups.
- **Scatter**: relationships between two variables.
- **Bridge (waterfall)**: reconcile a change (e.g., net income) into additive components.

Labeling rules
^^^^^^^^^^^^^^

- Title required.
- X and Y labels required.
- Include units in labels where possible (e.g., “Days”, “$”, “%”).
- Legends only when multiple series are present.
- Month labels should be shown as ``YYYY-MM``.

Axis guardrails
^^^^^^^^^^^^^^^

- **Bar charts start at zero** (default guardrail against y-axis tricks).
- Avoid dual axes.
- For ratio charts (margins, growth), include a **0 reference line** when helpful.

Distributions (e.g., A/R payment lag)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Skewed business distributions (like days-to-pay) should be communicated using a
**pair** of views:

- Histogram + vertical markers for **mean**, **median**, and a tail marker such as **p90**.
- ECDF to reveal tails (e.g., “90% of payments are within X days”).

Chapter outputs
---------------

Running Chapter 9 writes these outputs to the chosen ``outdir``:

- ``ch09_style_contract.json``
  - The style contract rules in a portable format.
- ``ch09_figures_manifest.csv``
  - A manifest (audit log) of each figure: filename, chart type, labels, and guardrail note.
- ``ch09_executive_memo.md``
  - A “10-bullet max” executive memo generated from the same inputs.
- ``ch09_summary.json``
  - A small structured summary (paths + counts).
- ``figures/*.png``
  - The example chart pack:

    - ``kpi_revenue_net_income_line.png``
    - ``kpi_margins_line.png``
    - ``ar_dso_line.png``
    - ``ar_days_hist.png``
    - ``ar_days_ecdf.png``
    - ``net_income_bridge.png``

How to run
----------

From the repo root (Windows / Git Bash):

.. code-block:: bash

   python -m scripts.business_ch09_reporting_style_contract \
     --datadir data/nso_v1 \
     --outdir outputs/track_d/ch09 \
     --seed 123

The command expects **NSO v1** simulator exports in ``--datadir``.
Chapter 9 reuses Chapter 8’s computations (KPIs + A/R metrics) and focuses on
consistent presentation.

Reading the manifest
--------------------

The manifest exists so a reviewer can answer:

- What chart type was used?
- Are labels present?
- Is there an explicit note when a guardrail matters?

In practice, this makes visual outputs auditable during code review.

Visualization pitfalls (“chart crimes”)
---------------------------------------

Common problems this chapter is designed to prevent:

- **Y-axis truncation in bar charts** to exaggerate differences.
- **Ambiguous labels** (“Revenue” without units, unclear time period).
- **Cherry-picked time windows** that hide seasonality or volatility.
- **Smoothing away volatility** that management should see.
- **Dual-axis charts** that encourage accidental correlation.

End-of-chapter problems
-----------------------

1) Chart correction
^^^^^^^^^^^^^^^^^^^

You are given three misleading charts (examples might include a truncated bar
chart or an over-smoothed line chart).

Task:

- Rebuild each chart using Chapter 9 helpers.
- Add a one-paragraph justification explaining what was misleading and how you fixed it.

Deliverable:

- “Before” (original) + “After” (corrected) figures.
- A short justification that references the style contract guardrails.

2) Variance waterfall (“bridge chart”)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A bridge chart explains *how* a value changed from one period to the next.
It reduces storytelling bias because the components must reconcile to the start
and end totals.

In this repo, Chapter 9 ships an **audit-friendly net income bridge**:

- Start: prior month net income
- Components: revenue change, COGS change, operating expense change
- Residual: “Other / rounding” to reconcile exactly (if needed)
- End: latest month net income

Task:

- Review the generated bridge chart and confirm the sign conventions.
- Write a short paragraph summarizing the dominant drivers.

Deliverable:

- ``figures/net_income_bridge.png``
- 1 paragraph interpretation (no false precision)

3) The 10-bullet memo
^^^^^^^^^^^^^^^^^^^^^

Write a narrative executive summary based on a provided chart pack.

Rules:

- Maximum 10 bullets.
- Every bullet must reference a chart or a metric.
- No false precision (prefer rounding: “$1.0M” instead of “$1,000,043.22”).

Deliverable:

- A markdown memo.
- Include a short “assumptions and caveats” section.

What’s next
-----------

Chapter 10 will build on this chapter by translating distributions into
**probability-and-risk statements** (e.g., “we will miss payroll 1 out of 20
months”) and by communicating uncertainty without false precision.
