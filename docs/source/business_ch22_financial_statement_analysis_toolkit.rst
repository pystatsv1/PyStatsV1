Business Statistics & Forecasting for Accountants (Track D)
===========================================================

Chapter 22 — Financial statement analysis toolkit (ratios, trends, variance, common-size)
-----------------------------------------------------------------------------------------

.. |trackd_run| replace:: d22
.. include:: _includes/track_d_run_strip.rst

This chapter is the "accountant's explainer pack": a small set of repeatable analyses that
turn monthly statements into decision support:

* **Ratios** — liquidity, leverage, profitability, and efficiency
* **Trends** — levels + percent changes (with rolling summaries)
* **Common-size statements** — normalize the income statement to revenue and the balance sheet
  to total assets so comparisons are apples-to-apples
* **Variance bridges** — a simple "what drove the change" decomposition month-over-month

The goal is not to "win" with a single metric. It's to build a **defensible story** that
avoids overclaiming.

Learning objectives
^^^^^^^^^^^^^^^^^^^

By the end of Chapter 22 you should be able to:

* Compute and interpret a core ratio set (liquidity, leverage, profitability, efficiency).
* Use common-size statements to explain *composition* changes, not just level changes.
* Build a simple variance bridge for net income (revenue vs costs).
* Identify "cosmetic" improvements (profit up, but working capital or cash risk worse).

NSO tables used
^^^^^^^^^^^^^^^

This chapter uses the NSO v1 synthetic tables:

* ``statements_is_monthly.csv`` — income statement (Sales Revenue, COGS, Operating Expenses, Net Income)
* ``statements_bs_monthly.csv`` — balance sheet (Cash, AR, Inventory, AP, taxes payable, notes payable, equity)
* ``statements_cf_monthly.csv`` — cash flow bridge (Net Change in Cash)

How to run
^^^^^^^^^^

From the repo root:

.. code-block:: bash

   # (Re)generate NSO v1 synthetic data (if needed)
   make business-nso-sim

   # Run Chapter 22
   make business-ch22

Outputs
^^^^^^^

Artifacts are written under ``outputs/track_d/``:

* ``ch22_ratios_monthly.csv`` — monthly ratio panel (liquidity, leverage, margins, working-capital days)
* ``ch22_common_size_is.csv`` — income statement common-size (percent of revenue)
* ``ch22_common_size_bs.csv`` — balance sheet common-size (percent of total assets)
* ``ch22_variance_bridge_latest.csv`` — last month vs prior month net-income bridge components
* ``ch22_assumptions.csv`` — definitions + guardrails (what each metric means)
* ``ch22_design.json`` — reproducibility metadata (inputs + definitions)
* ``ch22_memo.md`` — short interpretation memo
* ``ch22_figures_manifest.csv`` + ``figures/ch22_fig_*.png`` — figure list + plots

Interpretation guardrails
^^^^^^^^^^^^^^^^^^^^^^^^^

* **Don't overclaim**: ratios summarize relationships in the data; they don't prove causes.
* **Watch denominators**: small revenue months can inflate percentages.
* **Use context**: if net income improves but AR days rise, you may have a collections problem.
* **Check cash**: profits can improve while cash gets tighter due to working capital.

End-of-chapter problems
^^^^^^^^^^^^^^^^^^^^^^^

1. **Ratio set**: Compute a ratio panel (liquidity, leverage, profitability, efficiency) for two
   periods and identify tradeoffs and red flags.
2. **Common-size comparison**: Produce common-size statements for two periods and explain what
   changed strategically (mix, cost structure, or investment).
3. **Variance explanation tree**: Build a simple net income bridge (revenue, COGS, opex) and write
   a short explanation of the change with operational driver hypotheses.
