=============================================================
Chapter 8 -- Descriptive Statistics for Financial Performance
=============================================================

.. |trackd_run| replace:: d08
.. include:: _includes/track_d_run_strip.rst

By Chapter 7 we have an *analysis-ready* General Ledger:

* ``gl_tidy.csv`` -- line-level tidy GL (one row per journal line)
* ``gl_monthly_summary.csv`` -- monthly rollup by account

Chapter 8 answers the next practical question:

**"Now that the accounting data is tidy, how do we summarize performance and
variability in a way that helps business decisions?"**

This chapter focuses on descriptive statistics that accountants use every day:

* level (mean / median)
* spread (variance / standard deviation, coefficient of variation)
* tails and skew (quantiles; why "average" can be misleading)
* simple stability checks (rolling mean / rolling std; z-score style flags)

It also includes an A/R-focused section because receivables are a common source
of cash-flow surprises in small business.


Learning goals
==============

Accounting goals
---------------

* Turn monthly financial statements into *KPIs* (gross margin %, net margin %, etc.).
* Use variability measures to reason about operational stability.
* Connect A/R behavior to cash-flow risk using practical metrics:

  * credit sales vs collections
  * A/R ending balance and approximate Days Sales Outstanding (DSO)
  * a simple *FIFO application* of collections to invoices to estimate a
    distribution of "days outstanding".

Python/data goals
-----------------

* Convert long-form statement tables to wide data for analysis (``pivot_table``).
* Compute rolling statistics with ``Series.rolling``.
* Build "analysis artifacts" as CSV + a JSON summary/data dictionary.
* Keep scripts deterministic and testable.


Inputs
======

Chapter 8 reads from the NSO v1 synthetic dataset:

* ``chart_of_accounts.csv``
* ``gl_journal.csv``
* ``statements_is_monthly.csv``
* ``statements_bs_monthly.csv``
* ``ar_events.csv`` (added in Chapter 6)


Outputs
=======

This chapter writes the following files to ``outputs/track_d``:

``gl_kpi_monthly.csv``
  A compact monthly "performance dashboard" built from Income Statement +
  Balance Sheet lines. Includes ratios and rolling statistics.

``ar_monthly_metrics.csv``
  Monthly receivables metrics:

  * credit sales vs collections (from GL)
  * A/R beginning, ending, average (from B/S)
  * A/R turnover and approximate DSO

``ar_payment_slices.csv``
  **Optional-but-recommended** detail table. Each row represents a slice of a
  collection applied to an invoice under a FIFO assumption. This produces a
  realistic "days outstanding" distribution even when cash receipts do not
  explicitly reference invoice numbers.

``ar_days_stats.csv``
  Descriptive stats for "days outstanding" overall and by customer.

``ch08_summary.json``
  Summary metrics, checks, and a data dictionary.


How to run
==========

From the repository root:

.. code-block:: bash

   # 1) (Re)generate the NSO v1 synthetic dataset
   make business-nso-sim

   # 2) Run Chapter 8
   make business-ch08

   # 3) Inspect outputs
   ls outputs/track_d | grep -E "gl_kpi_monthly|ar_monthly_metrics|ar_days_stats|ch08_summary"


How to interpret the results
============================

KPIs: level vs variability
--------------------------

Two businesses can have the same *average* gross margin but very different risk
profiles.

* If ``gross_margin_pct_std_w3`` is high, margin is unstable -- pricing, input
  costs, and product mix might be swinging month to month.
* ``gross_margin_pct_cv`` (coefficient of variation) normalizes volatility by
  the mean and is useful when comparing different scales.

A/R: why "average DSO" can hide tails
-----------------------------------

The **mean** days outstanding can be pulled upward by a few very late payments.
The **median** is often a better "typical" payment time.

In ``ar_days_stats.csv`` look for:

* ``p90_days`` / ``p95_days`` -- tail risk (customers who pay very late)
* differences between mean and median -- skewness

The table ``ar_monthly_metrics.csv`` is your month-by-month monitoring view.
Large DSO spikes (or big gaps between credit sales and collections) are often
early warnings for cash-flow pressure.


Data dictionary highlights
==========================

``gl_kpi_monthly.csv``
  * ``gross_margin_pct`` = ``gross_profit / revenue``
  * ``net_margin_pct`` = ``net_income / revenue``
  * ``*_mean_w3`` and ``*_std_w3`` are 3-month rolling statistics

``ar_monthly_metrics.csv``
  * ``credit_sales`` = increase in A/R from invoices (GL A/R debits)
  * ``collections`` = decrease in A/R from cash collections (GL A/R credits)
  * ``dso_approx`` = ``avg_ar / credit_sales * days_in_month``

``ar_payment_slices.csv``
  * ``days_outstanding`` is computed as ``payment_date - invoice_date``
  * rows are *amount-weighted* payment slices created by FIFO application



Appendix
--------

See :doc:`business_appendix_ch08_milestone_big_picture` for a big-picture recap of Chapters 1-8 and a roadmap beyond Chapter 8.

Next chapter
============

Chapter 9 focuses on **visualization and reporting that doesn't mislead**.
Using the KPIs and A/R artifacts from Chapter 8, we standardize how figures
are labeled, how axes are handled (to avoid "chart crimes"), and how to produce a
compact executive memo that tells a coherent story from a small chart pack.

