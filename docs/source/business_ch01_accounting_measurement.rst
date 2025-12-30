.. _business-ch01:

Ch 01 — Accounting as a measurement system
=========================================

Why this matters (for accountants)
---------------------------------
Statistics is only useful if the underlying numbers are *meaningful* and *defensible*.
Accounting is the measurement layer that makes business analysis possible.

In other words:

* Bookkeeping creates the **data-generating process**.
* Accounting rules define what your measurements *mean*.
* Controls and ethics determine whether the measurements are trustworthy.

PyStatsV1’s promise is that we treat analysis like production software:

**Don’t just calculate your results — engineer them. We treat statistical analysis like production software.**

In Track D, that means every chapter is designed to be:

* **reproducible** (seeded simulation, deterministic reruns),
* **traceable** (inputs → transformations → outputs),
* **controls-aware** (reconciliation checks and “what could go wrong?”), and
* **decision-focused** (you end with a short memo, not just numbers).


Learning objectives
-------------------
By the end of this chapter, you will be able to:

1. Explain accounting as measurement (not just compliance).
2. Use the accounting equation to interpret business events.
3. Describe the core bookkeeping artifacts (journal, ledger, trial balance, statements).
4. Run a reproducible “mini-close” using PyStatsV1: simulate a tiny ledger, produce statements,
   and validate the accounting identity checks.


Core terms (fast refresher)
---------------------------

The accounting equation
^^^^^^^^^^^^^^^^^^^^^^^

.. math::

   \text{Assets} = \text{Liabilities} + \text{Equity}

This equation is the integrity constraint behind a balance sheet.

* **Assets**: resources the business controls (cash, receivables, inventory, equipment).
* **Liabilities**: obligations the business owes (accounts payable, loans, taxes payable).
* **Equity**: the residual claim (owner contributions + retained earnings).

Revenue, expense, and profit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Revenue** is value earned from customers.
* **Expenses** are resources consumed to generate revenue.
* **Net income** (profit) is revenue minus expenses for a period.

Double-entry bookkeeping
^^^^^^^^^^^^^^^^^^^^^^^^

Every transaction is recorded with at least two entries:

* total **debits** = total **credits** within each transaction, and
* the system stays consistent with the accounting equation.

Key artifacts
^^^^^^^^^^^^^

* **Journal entry**: one transaction recorded as debit/credit lines.
* **General ledger (GL)**: all journal lines organized by account.
* **Trial balance**: account totals used to validate that debits = credits.
* **Financial statements**: summarized views for decision making (income statement, balance sheet).

Accrual vs cash timing (one idea to keep in mind)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Accounting often records economic activity when it is **earned/incurred** (accrual basis),
not necessarily when cash moves. This matters later for forecasting, because:

* profit does **not** equal cash, and
* timing choices can create “patterns” that are artifacts of close processes.


Accounting Connection (PDF refresher)
-------------------------------------
This chapter refreshes the PDF’s **Bookkeeping basics** pillar:

* accounting as measurement,
* the bookkeeper’s role in financial integrity,
* the double-entry method,
* the GL and financial statements as outputs.


Dataset tables used (LedgerLab core)
------------------------------------
In Track D we use a synthetic, accounting-shaped dataset family sometimes referred to as **LedgerLab**.

For Chapters 1–3 we start with a **small “core ledger” dataset** (e.g., ``ledgerlab_ch01``).
Starting in later chapters, Track D’s default running case becomes **North Shore Outfitters (NSO v1)**
written to ``data/synthetic/nso_v1``.
In Chapter 1 we start small:

* ``chart_of_accounts.csv``
* ``gl_journal.csv`` (transaction-level debit/credit lines)
* ``trial_balance_monthly.csv``
* ``statements_is_monthly.csv`` (baseline month)
* ``statements_bs_monthly.csv`` (baseline month)


What you’ll build in this chapter
---------------------------------
You will run a “mini-close” workflow:

1. **Simulate** a small month of accounting activity (seeded and reproducible).
2. **Generate** a trial balance and basic statements.
3. **Validate** core integrity checks:

   * debits = credits per transaction,
   * the accounting equation balances on the balance sheet.

4. **Summarize** the month with a few “accountant-friendly” descriptive statistics.


What the automated checks verify (exactly)
------------------------------------------
When you run ``make business-ch01``, the script prints a small set of controls-style checks.
These checks are intentionally “audit-friendly”: they tell you whether the accounting data
is internally consistent before you trust any statistics or forecasts derived from it. 

These appear under “Checks:” in the console output.

Double-entry transaction check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``transactions_balanced``: for every ``txn_id``, sum(debits) == sum(credits).
  (If this fails, the GL is not a valid double-entry ledger.)

  Companion diagnostics:
  - ``n_transactions``: number of transactions observed
  - ``n_unbalanced``: number of transactions failing the rule
  - ``max_abs_diff``: worst imbalance magnitude (0.0 is ideal)

Accounting equation tie-out (balance sheet identity)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``accounting_equation_balances``: verifies the balance sheet integrity constraint:

  .. math::

     \text{Total Assets} = \text{Total Liabilities + Equity}

  Companion diagnostics:
  - ``total_assets``: computed total assets
  - ``total_liabilities_plus_equity``: computed total liabilities + equity
  - ``abs_diff``: absolute difference between the two totals (0.0 is ideal)

Small nonzero differences extremely close to 0 can occur due to floating-point arithmetic; treat anything near machine precision as “effectively zero.”

If a check fails, treat it like a controls exception:
trace back to the offending transaction(s), confirm sign conventions, and verify statement rollups.


PyStatsV1 lab (Run it)
----------------------

Using Makefile targets (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-sim
   make business-ch01

Using Python module commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 1) Simulate the LedgerLab *core* dataset (Chapter 1 needs only the core tables)
   python -m scripts.sim_business_ledgerlab \
     --outdir data/synthetic/ledgerlab_ch01 \
     --seed 123 \
     --month 2025-01 \
     --n-sales 18

   # 2) Analyze Chapter 1 and write a summary JSON + plots
   python -m scripts.business_ch01_accounting_measurement \
     --datadir data/synthetic/ledgerlab_ch01 \
     --outdir outputs/track_d \
     --seed 123

Outputs you should see
^^^^^^^^^^^^^^^^^^^^^^

* Console output showing the integrity checks and key month metrics.
* A LedgerLab core dataset folder in ``data/synthetic/ledgerlab_ch01``.
* (Later) the NSO v1 running case in ``data/synthetic/nso_v1``.
* A chapter output folder in ``outputs/track_d`` containing:

  * ``business_ch01_summary.json``
  * ``business_ch01_cash_balance.png``
  * ``business_ch01_balance_sheet_bar.png``



How to modify the scripts (student exercises)
---------------------------------------------

1) Change the business story
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``scripts/sim_business_ledgerlab.py`` and try changing:

* the number of sales (``--n-sales``),
* the average sale amount,
* the fraction of sales on account (AR vs cash), or
* the mix of expenses.

Then rerun the simulator and Chapter 1 analyzer.

2) Add your own integrity check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ``scripts/business_ch01_accounting_measurement.py``:

* add a new check to flag negative inventory,
* validate that revenue is never negative,
* or compute a simple KPI like gross margin percentage.


Interpretation & decision memo
------------------------------

After you run the lab, answer these memo prompts in 6–10 sentences:

1. **Measurement:** What does the accounting equation tell you about this business month?
2. **Trust:** Do the integrity checks pass? If they failed, what is the most likely root cause?
3. **Decision support:** Based on revenue, expenses, and cash balance, what is one action you would recommend?
4. **Forecasting preview:** Which number in the statements would you most want to forecast next, and why?


End-of-chapter problems
-----------------------

1) Accounting equation classification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Classify each event as increasing/decreasing assets, liabilities, or equity:

* owner contributes cash,
* inventory purchase on credit,
* customer sale on account,
* collecting on AR,
* paying AP,
* recording rent expense.

2) Timing and classification gotchas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For each scenario, describe how it can distort analytics:

* a large invoice posted in the wrong month,
* an expense miscoded to the wrong account,
* missing documentation requiring later reclass,
* a bank reconciliation not performed.

3) PyStatsV1 reproducibility note
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Write a short policy (8–12 lines) for how your team will ensure:

* every analysis can be rerun,
* outputs are saved with metadata (seed, run date, code version), and
* changes are reviewed like production code.


What’s next
-----------

Chapter 2 treats the general ledger as a dataset: we’ll structure it for analysis, build
clean extracts, and set up “analysis-friendly” conventions that make forecasting chapters
much easier.


Textbook alignment notes
------------------------
Textbook Part A: Chapters 1–3.