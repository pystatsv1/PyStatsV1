Business Chapter 7: Preparing accounting data for analysis
==========================================================

.. |trackd_run| replace:: d07
.. include:: _includes/track_d_run_strip.rst

This chapter is the “bridge” between bookkeeping outputs (CSV exports, trial
balances, etc.) and the kinds of tables you want for statistics, forecasting,
and dashboards.

In real organizations, *data prep* is often the highest-leverage work:

- Raw general ledger exports are not model-friendly.
- The chart of accounts (COA) contains the semantic labels you need.
- Most analytics workflows want *one amount column*, not separate debit/credit.

Chapter 7 produces two small, reusable datasets:

- **gl_tidy.csv** (line-level): one row per GL line, with COA labels
  and a single signed amount.
- **gl_monthly_summary.csv** (rollup): a monthly activity table by account.

What you should be able to do after this chapter
-----------------------------------------------

- Explain why accountants track debits/credits, but analysts often prefer one
  signed amount column.
- Build a tidy, analysis-ready GL table that preserves auditability.
- Create a monthly roll-up suitable for time-series work and forecasting.
- Run basic data-quality checks before modeling.

Inputs and outputs
------------------

Inputs (from the NSO v1 dataset folder)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``gl_journal.csv``: the line-level journal export
- ``chart_of_accounts.csv``: the COA lookup table

Outputs (written to ``--outdir``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``gl_tidy.csv``
- ``gl_monthly_summary.csv``
- ``ch07_summary.json`` (counts + light QC signals)

Running the chapter
-------------------

If you have not generated the NSO v1 dataset yet:

.. code-block:: bash

   make business-nso-sim

Then run Chapter 7:

.. code-block:: bash

   make business-ch07

Or run the module directly:

.. code-block:: bash

   python -m scripts.business_ch07_preparing_accounting_data_for_analysis \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

The two output tables
---------------------

1) ``gl_tidy.csv`` (line-level)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *raw* GL has ``debit`` and ``credit`` columns. That is perfect for
accounting integrity, but awkward for analysis.

In ``gl_tidy.csv`` we keep the audit fields (``txn_id``, ``doc_id``, ``date``,
``description``) and add COA labels:

- ``account_name``
- ``account_type``
- ``normal_side`` (debit or credit)

We also add two derived amount fields:

- ``raw_amount`` = ``debit - credit`` (debit positive, credit negative)
- ``amount`` = signed change in the account’s **normal-side** direction

Why two amount columns?

- ``raw_amount`` is a faithful numeric encoding of the journal line.
- ``amount`` is usually what you want for analytics (“did the account go up or
  down, in the normal direction?”).

To make each row easy to reference, we add:

- ``line_no``: the line number within a transaction
- ``gl_line_id``: ``<txn_id>-<line_no>``

2) ``gl_monthly_summary.csv`` (monthly roll-up)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a grouped summary of the tidy GL:

- group by ``month`` + account
- sum ``debit``, ``credit``, and ``amount``

This produces a table that is immediately useful for:

- trend charts and dashboards
- anomaly detection (spikes in monthly activity)
- forecasting models (per-account time series)

Reading ``ch07_summary.json``
-----------------------------

The summary JSON is a small “run report” that answers:

- How many rows were produced?
- Did we successfully join to the COA?
- Did we have any unparseable dates?

It is not meant to be exhaustive; it is meant to provide quick confidence
before you begin deeper analysis.

Exercises and extensions
------------------------

1. **Wide-format features:** pivot ``gl_monthly_summary.csv`` so each account is
   a column and each month is a row. (This is a common forecasting feature
   matrix.)
2. **Custom groupings:** map accounts into “management categories” (e.g.,
   *marketing spend*, *shipping expense*) and create a second monthly summary.
3. **More QC checks:** add rules to flag months where an expense account has
   negative activity, or where an account has no COA mapping.

Notes for maintainers
---------------------

- Keep ETL helpers small and testable. Shared code lives in
  ``scripts/_business_etl.py``.
- Prefer deterministic outputs (stable sorting, fixed seed). It keeps unit tests
  robust and makes docs examples repeatable.
