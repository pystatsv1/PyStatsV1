.. _track_d_my_own_data:

============================================
Track D: Apply what you learned to your data
============================================

This page is the “bridge” between *the Track D running case* (NSO v1 + LedgerLab)
and your own accounting / bookkeeping / finance data.

**Goal:** take the same analyst habits you practiced in Track D (contracts, checks, joins,
reproducible outputs, and clear communication) and apply them to real data responsibly.

If you haven’t yet, start here:

- :doc:`track_d_student_edition` (Student Edition entry point)
- :doc:`track_d_dataset_map` (dataset mental model: tables, keys, intentional QC “warts”)
- :doc:`track_d_outputs_guide` (what each output file means and how to read it)

What “your own data” usually looks like
=======================================

Most student projects look like one of these:

1) **Accounting exports**
   - QuickBooks / Xero exports (GL detail, trial balance, A/R aging, A/P aging)
   - Bank CSV exports (transactions, balances)
   - Payroll exports (wage detail, remittances)

2) **Operational tables that explain the numbers**
   - invoices / sales orders
   - purchase orders
   - inventory movements
   - time sheets / payroll runs

3) **A “chart of accounts”**
   - account_id + account_name + type (“Asset”, “Liability”, …)

The Track D case teaches you how to *think in tables*:
each table has a grain, keys, expected constraints, and known failure modes.

The rule: do NOT start with modeling — start with contracts
===========================================================

Before you run any stats, write down:

- **What is a row?** (grain)
- **What uniquely identifies a row?** (primary key)
- **What columns are required?**
- **What values are allowed?** (domain checks)
- **What must be true across tables?** (invariants)

This is what turns you into an “accounting-data analyst” instead of a “Python runner.”

A practical workflow you can reuse
==================================

Step 0 — Make a safe copy
-------------------------

Work on a copy of the data, not the original export.

- Remove names / sensitive fields if you’re sharing work.
- Keep a read-only “raw/” folder and an editable “working/” folder.
- Record the export date and the system (QuickBooks/Xero/bank).

Step 1 — Normalize column names
-------------------------------

Real exports have messy headers.
Pick one naming style (snake_case is easiest) and normalize:

- ``Invoice #`` → ``invoice_id``
- ``Txn Date`` → ``date``
- ``Customer`` → ``customer``

Tip: keep a small mapping note in your project folder (even a plain text file).

Step 2 — Convert money fields to numeric
----------------------------------------

Accounting exports often include:

- currency symbols (``$1,234.56``)
- parentheses for negatives (``(123.45)``)
- commas as thousands separators

Convert these into numeric columns early, and confirm:

- missing values are handled
- signs are correct
- totals match the source system

Step 3 — Build “checkpoint” tables
----------------------------------

The Track D case repeatedly uses “checkpoint” tables:

- **GL journal** (debits/credits by txn)
- **Trial balance** (ending balances by account)
- **Statements** (IS/BS/CF rollups by month)

For your own data, try to create at least one checkpoint table that you trust
(e.g., a Trial Balance export) so you can validate your reconstruction.

Step 4 — Run the minimum set of QA checks
-----------------------------------------

Borrow these habits from Track D:

- **Uniqueness checks:** keys unique (no duplicate IDs)
- **Completeness:** required columns non-null
- **Range checks:** dates in expected window, amounts not absurd
- **Reconciliation checks:** totals tie out
- **Invariants:** debits = credits; Assets = Liabilities + Equity (when applicable)

Document failures. In accounting analytics, failures are often the most useful results.

Step 5 — Only then: analysis + story
------------------------------------

Once the data is clean enough, the “stats” becomes meaningful:

- trends (month-over-month)
- segmentation (customer/vendor/product)
- variability (outliers, tails, seasonality)
- drivers (regression with careful interpretation)
- risk (probability of cash shortfalls, DSO tails)

How to translate Track D tables to your tables
==============================================

Use the mental model page as your guide:

- :doc:`track_d_dataset_map`

**You don’t need every table.**
Pick the tables that let you answer your question *and* support validity checks.

Examples:

- If your goal is **cash forecasting**, you need bank transactions + expected inflows/outflows.
- If your goal is **A/R collection analysis**, you need invoices + collections + customer IDs.
- If your goal is **profitability diagnostics**, you need revenue + COGS + operating expenses, ideally by month.

What to do when the data is “weird”
===================================

Track D intentionally includes “warts” to train you.

Real data has the same issues, and the response is the same:

- Identify the anomaly
- Explain why it matters
- Decide whether to fix, exclude, or model it explicitly
- Document the decision

Common “weird” patterns:

- duplicate transaction IDs
- negative inventory (timing, stockouts, backorders)
- negative A/R (credits, misapplied payments)
- month boundary issues (late postings, backdated entries)

A responsible sharing checklist
===============================

Before you share a report, make sure you can answer:

- What data source(s) did you use and when was it exported?
- What transformations did you apply?
- What checks did you run, and what failed?
- What limitations remain?
- What decisions might change if the data is incomplete?

Next steps
==========

If you want a guided assignment structure, see the upcoming Track D assignment pages
(coming as separate docs PRs) that include:

- a “my own data” project template
- a rubric that rewards good contracts + checks + communication
- example memos and charts that avoid common mistakes

For now, you can still practice the core workflow by using Track D’s reproducible case
and mirroring the same steps with your own exports.
