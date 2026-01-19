Track D Dataset Map
===================

This page gives you a **dataset mental model** for Track D.

If Track D is “learn to analyze accounting data,” then this page is the **map**:

* what each table is,
* how tables relate,
* and why some rows look “wrong” on purpose (because real data is messy).

.. tip::

   Run ``pystatsv1 workbook run d00_peek_data`` first.
   It prints a quick preview of the tables and writes a short summary markdown file
   under ``outputs/track_d``.

Where the datasets live
-----------------------

When you run:

* ``pystatsv1 workbook init --track d``

...the workbook starter is created and the canonical (seeded) Track D datasets are
installed into the workbook folder under:

* ``data/synthetic/ledgerlab_ch01/``
* ``data/synthetic/nso_v1/``

These are small, deterministic datasets (seed=123) designed for learning.

Two dataset families
--------------------

Track D uses two dataset families:

1) **LedgerLab (Ch01)**: a compact “toy business” general ledger example.
2) **NSO v1 running case**: a larger, more realistic multi-module accounting dataset
   (A/R, A/P, bank, inventory, payroll, taxes, schedules) that rolls up into a general
   ledger and financial statements.

The point of using *two* datasets is deliberate:

* LedgerLab teaches the **accounting database basics**.
* NSO v1 trains you to think like an **accounting-data analyst** in a messy, realistic
  environment.

Two dataset families
--------------------

Track D ships two canonical datasets (both deterministic with ``seed=123``):

1) **LedgerLab (Ch01)** — a small, clean “training ledger.”
2) **NSO v1 running case** — a larger, more realistic operating dataset (AR/AP, bank, inventory, payroll, tax, schedules).

You will use both:

* LedgerLab is where you learn the **accounting invariants** and the “shape” of ledger data.
* NSO is where you practice **being an accounting-data analyst**: messy source tables, reconciliations, and quality control.


LedgerLab (Ch01): COA → GL → TB → Statements
--------------------------------------------

LedgerLab is intentionally small so you can see the whole pipeline at once.

::

   chart_of_accounts.csv
          |
          v
   gl_journal.csv  (journal lines: debits/credits)
          |
          v
   trial_balance_monthly.csv
          |
          v
   statements_is_monthly.csv
   statements_bs_monthly.csv
   statements_cf_monthly.csv

**What the tables mean**

``chart_of_accounts.csv``
  The chart of accounts (COA): the “dictionary” of accounts.

``gl_journal.csv``
  The general ledger journal in long format.

  * One business transaction (``txn_id``) typically appears as **multiple lines**.
  * Debits and credits should balance **within each ``txn_id``**.
  * Lines carry account metadata (name/type/normal side) to make analysis easier.

``trial_balance_monthly.csv``
  A monthly trial balance per account.

  * It aggregates the journal by account and month.
  * It exposes the **ending balance** and the **ending side** (Debit/Credit).

``statements_*_monthly.csv``
  Monthly financial statement lines.

  * IS: revenue, COGS, expenses, net income
  * BS: assets, liabilities, equity totals
  * CF: net income plus working-capital deltas

**Why LedgerLab matters**

Before you can analyze “business performance,” you must trust the accounting pipeline.
LedgerLab lets you practice asking:

* “Is each transaction balanced?”
* “Does the accounting equation hold?”
* “Do TB and statements agree?”

Those checks show up in the Track D workbook outputs and are part of what makes you a stronger analyst.

NSO v1 running case
-------------------

NSO v1 is a **running business case** designed to look like the output of several operational systems.
In real organizations, you rarely start from a clean GL export.
You start from **subledgers and operational logs**, then reconcile and validate.

The NSO flow (high level)
^^^^^^^^^^^^^^^^^^^^^^^^^

In NSO, the operational tables describe what happened. The GL journal is the accounting translation.

::

   (AR events)        (AP events)        (Bank statement)
        \                 |                    /
         \                |                   /
          v               v                  v
     (Inventory movements)   (Payroll + tax)   (Schedules)
                 \             |               /
                  \            |              /
                   v           v             v
                       gl_journal.csv
                             |
                             v
                     trial_balance_monthly.csv
                             |
                             v
          statements_is_monthly.csv / statements_bs_monthly.csv / statements_cf_monthly.csv

Source tables (what they represent)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below is a quick “what is this?” guide. These are the tables you analyze, reconcile, and use to build features.

``ar_events.csv``
  Customer invoices and collections.

  * Invoices increase A/R (``ar_delta`` positive).
  * Collections decrease A/R and increase cash received.

``ap_events.csv``
  Vendor invoices and payments.

  * Invoices increase A/P (``ap_delta`` positive).
  * Payments reduce A/P and reduce cash.

``bank_statement.csv``
  What the bank says happened.

  * One row per bank posting (cash in/out).
  * ``gl_txn_id`` links a bank row to the accounting transaction that explains it.

``inventory_movements.csv``
  Purchases and sales issues by SKU.

  * Purchases add units and cost.
  * Sales issues remove units and cost.

``payroll_events.csv``
  Payroll accruals, withholding, employer taxes, and cash payments.

``sales_tax_events.csv``
  Sales tax collected (liability increases) and remittances (liability decreases).

``fixed_assets.csv``
  Asset master file (what was purchased, when it went into service, and how it should be depreciated).

``depreciation_schedule.csv``
  The depreciation schedule (a helper table you can audit).

``debt_schedule.csv``
  Loan activity: beginning balance, interest, principal, ending balance.

``equity_events.csv``
  Owner contributions and draws.

Accounting output tables
^^^^^^^^^^^^^^^^^^^^^^^^

Just like LedgerLab, NSO has accounting outputs:

* ``gl_journal.csv`` — the accounting translation in long format
* ``trial_balance_monthly.csv`` — monthly balances per account
* ``statements_*_monthly.csv`` — monthly statement lines

Your job in Track D is to learn how to:

* explain statements using the underlying operational tables,
* reconcile cash and working-capital movements,
* and detect data quality problems before they mislead your analysis.

Keys and joins cheat sheet
--------------------------

Most Track D work is “join, aggregate, compare.” These keys show up across tables.

.. list-table:: Keys you will use again and again
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Meaning and typical use
   * - ``month``
     - Accounting/reporting period in ``YYYY-MM`` format. Use it to group, pivot, and line up monthly outputs.
   * - ``txn_id``
     - The **accounting transaction id**. In ``gl_journal.csv`` it identifies all lines that belong to one balanced transaction.
   * - ``doc_id``
     - Human-friendly document id (invoice/payment/asset/etc.) often used to trace a transaction in reports.
   * - ``account_id``
     - Chart-of-accounts id. Join ``gl_journal.csv`` and ``trial_balance_monthly.csv`` to ``chart_of_accounts.csv`` on this.
   * - ``invoice_id``
     - Subledger document id for AR/AP. Often connects an invoice event to a later collection/payment event.
   * - ``bank_txn_id``
     - Bank-provided transaction identifier. Should be unique in a perfect world (but see the QC section below).
   * - ``gl_txn_id``
     - Link from a bank row back to the accounting transaction that explains it.
   * - ``sku``
     - Product identifier used to group inventory movements and compute unit economics.
   * - ``asset_id`` / ``loan_id``
     - Keys for fixed asset and debt schedules.

A practical join pattern
^^^^^^^^^^^^^^^^^^^^^^^^

A common Track D pattern is:

1) Start from a statement line (for example, ``Sales Revenue`` in ``statements_is_monthly.csv``).
2) Find the accounting lines that feed it (filter ``gl_journal.csv`` to revenue accounts).
3) Trace back to operational drivers (AR events, cash sales, product mix, seasonality).

This is the accounting-analyst version of “feature engineering.”

Intentional QC issues (the “warts”)
-----------------------------------

Some tables include a few “warts” on purpose.
They exist so you can practice the kind of quality-control checks analysts do in real jobs.

.. admonition:: Example warts you should notice
   :class: note

   * **Duplicate bank transaction id**

     In ``bank_statement.csv`` you should see a duplicated ``bank_txn_id`` row (it’s tagged in the description output by ``d00_peek_data``).
     This teaches you not to assume the bank feed is automatically clean.

   * **Negative inventory can appear**

     Inventory can go negative early in a period.
     That can mean a stockout, a late purchase posting, or a timing mismatch between operational and accounting systems.
     The analysis lesson is: *don’t hide it; explain it and measure its impact.*

   * **Aggregated rows vs. transactional rows**

     Some operational tables mix “transaction-like” rows with monthly totals.
     For example, ``sales_tax_events.csv`` can have collection rows without a concrete ``txn_id``.
     That teaches you to design joins carefully and document assumptions.

The point is not to “fix the dataset.”
The point is to learn to write analyses that remain correct even when the inputs are imperfect.

How to use this map in a lab
----------------------------

A simple lab rhythm that works well:

1) **Peek**: run ``d00_peek_data`` and skim the previews.
2) **Pick a question**: choose a business question (profitability, cash, working capital, seasonality, drivers).
3) **Choose a level**:

   * start at **statements** if you are answering an executive question,
   * start at **trial balance** if you are reconciling,
   * start at **operational tables** if you are building drivers.

4) **Trace and explain**:

   * statements \u2192 ledger lines (GL) \u2192 operational drivers,
   * and annotate any QC issues you encounter.

5) **Write the story**: the end product is a short, well-documented explanation.

For more detail on what each script writes to ``outputs/track_d/`` and how to read it, see:

* :doc:`track_d_outputs_guide`

If you want to run Track D on your own exported data later, see:

* :doc:`track_d_my_own_data`
