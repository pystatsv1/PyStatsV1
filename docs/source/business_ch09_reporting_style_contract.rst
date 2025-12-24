Business Chapter 9 — Plotting & reporting style contract
=======================================================

Chapter 9 has two goals:

1. Define a *style contract* for the Track D figures and short reports.
2. Produce a set of example figures (KPIs + A/R) that follow the contract.

Why a “style contract”?
-----------------------

In business analytics, the same *data* can look honest or misleading depending
on presentation. A consistent contract makes results:

- easier to compare across months/chapters,
- easier to audit,
- easier to re-run in CI without manual tweaks.

Inputs
------

This chapter reads the raw NSO v1 synthetic bookkeeping dataset (the same
folder used by Chapters 7–8). It internally calls Chapter 8 to compute KPIs
and A/R metrics.

Outputs
-------

The chapter writes a small figure set and metadata:

- ``figures/``

  - ``kpi_revenue_net_income.png``
  - ``kpi_margin_pct.png``
  - ``ar_dso_approx.png``
  - ``ar_days_hist.png``
  - ``ar_days_ecdf.png``

- ``ch09_figures_manifest.csv``
  One row per figure (filename, type, title/caption, labels, and source).

- ``ch09_style_contract.json``
  A machine-readable snapshot of the plotting contract.

- ``ch09_executive_memo.md``
  A compact, deterministic “one-page memo” with 10 bullets derived from the
  KPIs and A/R metrics (useful as a template for stakeholder updates).

- ``ch09_summary.json``
  Run report: row counts + a few basic checks.

The style contract
------------------

The contract is intentionally small. It answers: *what chart types do we allow
and what are the rules for each?*

Allowed chart types
~~~~~~~~~~~~~~~~~~~

- **Time-series line**: KPIs over time (optionally with a rolling average).
- **Bar chart**: categorical comparisons (must start y-axis at zero).
- **Histogram**: distributions (show mean/median markers).
- **ECDF**: distributions with tails (best for skew, like A/R days).
- **Box plot**: optional for multi-group comparisons.

Labeling rules
~~~~~~~~~~~~~~

- Title: clear, specific, no jargon.
- Axis labels include units (e.g., ``Days`` or ``$``).
- Percent values are shown as percent on the y-axis.
- For time series, the x-axis is month (``YYYY-MM``), with ticks rotated.

Avoiding misleading axes
~~~~~~~~~~~~~~~~~~~~~~~~

- **Bar charts** must start at zero.
- **Line charts** may use a focused y-range, but must show units and include a
  caption that the axis is not zero-based.
- Ratio charts (margins, growth) include a zero reference line.

Distributions (A/R days)
~~~~~~~~~~~~~~~~~~~~~~~

For skewed distributions:

1. Show a **histogram** with **mean** and **median** markers.
2. Show an **ECDF** and mark key quantiles (P50/P90) to highlight tails.

How to run
----------

From the project root:

.. code-block:: bash

   make business-nso-sim
   make business-ch09

Or run the script directly:

.. code-block:: bash

   python -m scripts.business_ch09_reporting_style_contract \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Next chapter
------------

Chapter 10 will use the same contract while introducing simple forecasting
baselines (moving averages / naive) and forecast accuracy reporting.
