Track D Lab 0/1 (PyPI-only)
===========================

TA Notes + Script for Explaining the Lab and the Outputs
--------------------------------------------------------

This handout is for a TA running a lab section where students install **PyStatsV1** from **PyPI**, initialize the
**Track D workbook**, and run:

- ``d00_peek_data`` (tour the datasets)
- ``d01`` (Chapter 1: accounting checks + key metrics)
- ``business_smoke`` (a short automated check suite)

It includes what to say, what students should see, and how to explain the output.

Recommended pre-reading (TA)
----------------------------

If you have 5 minutes before lab, skim these pages:

* :doc:`track_d_student_edition` — the “book-style” Track D entry point
* :doc:`track_d_dataset_map` — the table mental model + intentional QC “warts”
* :doc:`track_d_outputs_guide` — what each generated output means and how to interpret it
* :doc:`track_d_my_own_data` — a practical "bring your own data" bridge (30-minute recipe)
* :doc:`track_d_assignments` — classroom-ready labs + rubric (gradeable artifacts + short answers)

How to use the assignments page
-------------------------------

If you want Track D to be **turnkey as a lab**, point students at:

* :doc:`track_d_assignments`

That page is designed to be self-contained:

* **Lab 1**: run Track D and interpret outputs
* **Lab 2**: reconcile a teachable QC issue (duplicate bank transaction id)
* **Lab 3**: write a short executive summary memo from the outputs

The rubric is intended to reward analysis habits (contracts, checks, reconciliation, and clear writing),
not just code execution.

1. Learning goals
=================

By the end of this lab, students should be able to:

1. Set up a clean Python environment (virtualenv) for reproducible analysis.
2. Install a “batteries included” workbook from PyPI (no cloning repos).
3. Initialize a Track D project folder that contains:

   - a Track D workbook template
   - pre-installed synthetic datasets (seed=123)

4. Run a “data tour” to see what files exist and what they look like.
5. Run an “accounting data sanity check” and interpret the outputs:

   - Are entries balanced?
   - Does the accounting equation hold?
   - What are the basic business metrics?

6. Run a lightweight test suite (``business_smoke``) as a professional habit.

TA framing line
---------------

“Today isn’t about memorizing accounting terms. It’s about learning the analyst’s workflow:
install → initialize → inspect → validate → summarize → repeat.”

2. Lab structure
================

**Total time:** ~40–60 minutes

1) Setup (10–15 min)
   Create venv, upgrade pip, install ``pystatsv1[workbook]``.

2) Initialize workbook (5 min)
   Create a Track D workbook folder with datasets pre-installed.

3) Explore data (10–15 min)
   Run ``d00_peek_data``, interpret what’s in LedgerLab + NSO.

4) Run first analysis/checks (10 min)
   Run ``d01``, interpret checks + key metrics.

5) Confidence check (5 min)
   Run ``business_smoke`` and explain what “13 passed” means.

3. Environment setup talk track
===============================

3.1 Why virtual environments matter (30 seconds)
------------------------------------------------

“A virtual environment is a sealed sandbox. Everyone in this class can run the same commands and get the same results.
It prevents dependency conflicts and makes troubleshooting easier.”

3.2 Commands
------------

.. code-block:: bash

   python -m venv .venv
   # Windows (Git Bash):
   source .venv/Scripts/activate
   python -m pip install -U pip
   pip install "pystatsv1[workbook]"

What students should notice
---------------------------

- pip upgrades successfully.
- The install pulls scientific stack packages (NumPy/Pandas/SciPy/Statsmodels/Matplotlib…).
- The workbook extra includes ``pytest``, which powers ``workbook check``.

TA note: If installs are slow, reassure them it’s normal (large compiled wheels).

4. Initialize the Track D workbook
==================================

4.1 What ``init`` does
----------------------

“``workbook init`` creates a new project folder. It copies a starter template and unpacks the datasets into a predictable
location. You now have a ready-to-run lab workspace.”

.. code-block:: bash

   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

Students should see a message like:

- “✅ Track D workbook starter created at …”
- “Datasets are pre-installed under ``data/synthetic/``, seed=123.”

4.2 Why seed=123 matters
------------------------

“Seed=123 means the synthetic datasets are deterministic. If you and I run the same scripts, we get the same numbers.
That’s key for teaching, grading, and reproducibility.”

5. List the available Track D runs
==================================

.. code-block:: bash

   pystatsv1 workbook list --track d

Explain the list
----------------

- Each ``Dxx`` corresponds to a chapter or checkpoint.
- ``d00_peek_data`` is the dataset tour.
- ``d01`` is the first content chapter runner.
- Later chapters (``d02``–``d23``) provide a consistent “run menu” over the course.

TA line: “You can think of this as a menu of mini-programs: run, inspect outputs, then modify and extend.”

6. Run ``d00_peek_data`` (data tour)
====================================

.. code-block:: bash

   pystatsv1 workbook run d00_peek_data

6.1 What ``d00_peek_data`` is doing
-----------------------------------

Explain it as three steps:

1. Locate datasets under ``data/synthetic/…``
2. Read each CSV and print:

   - file name
   - number of rows/columns
   - column names
   - a small preview

3. Write a Markdown summary file:

   - ``outputs/track_d/d00_peek_data_summary.md``

TA line: “Before statistics, confirm what data exists and what shape it’s in.”

6.2 Two datasets: LedgerLab vs NSO
----------------------------------

LedgerLab (Ch01)
^^^^^^^^^^^^^^^^

LedgerLab is a small “training wheels” business dataset you can trace end-to-end:

- ``chart_of_accounts.csv`` (account dictionary)
- ``gl_journal.csv`` (debit/credit lines by transaction)
- ``trial_balance_monthly.csv`` (monthly balances)
- ``statements_is_monthly.csv`` (income statement)
- ``statements_bs_monthly.csv`` (balance sheet)
- ``statements_cf_monthly.csv`` (cash flow)

TA point: “LedgerLab helps you trace journal → trial balance → statements.”

NSO v1 running case
^^^^^^^^^^^^^^^^^^^

NSO is the “bigger business system” with multiple subledgers and derived outputs:

- ``bank_statement.csv`` (includes a deliberately duplicated ID)
- ``ar_events.csv`` / ``ap_events.csv``
- ``inventory_movements.csv``
- ``payroll_events.csv``
- ``sales_tax_events.csv``
- ``fixed_assets.csv`` + ``depreciation_schedule.csv``
- ``debt_schedule.csv``
- plus statement/trial balance outputs

TA point: “NSO is designed to feel like real company data: multiple sources and common quality issues.”

6.3 Key columns to explain
--------------------------

``chart_of_accounts.csv``
^^^^^^^^^^^^^^^^^^^^^^^^^

- ``account_type``: Asset, Liability, Equity, Revenue, Expense, Contra Asset
- ``normal_side``:

  - Assets/Expenses normally **Debit**
  - Liabilities/Equity/Revenue normally **Credit**

TA line: “Normal side is about sign conventions in the system.”

``gl_journal.csv``
^^^^^^^^^^^^^^^^^^

- ``txn_id`` groups multiple lines into one transaction.
- Each transaction should balance: sum(debits) = sum(credits).

TA line: “A transaction is a mini-equation: where value came from and where it went.”

Statements and trial balance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Trial balance is database-style output.
- Statements are human-facing summaries.

TA line: “Trial balance is the structured ledger; statements are the story.”

7. Run ``d01`` (Chapter 1 checks + key metrics)
===============================================

.. code-block:: bash

   pystatsv1 workbook run d01

It prints **Checks** and **Key metrics**, then writes artifacts under ``outputs/track_d``.
If students ask "what is this file?", point them to :doc:`track_d_outputs_guide`.

7.1 Checks (what they mean)
---------------------------

``transactions_balanced: True``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every transaction’s debits equal credits.

TA line: “If this fails, you fix the data pipeline before analysis.”

``n_transactions``
^^^^^^^^^^^^^^^^^^

Count of transaction groups in the LedgerLab data used for d01.

``n_unbalanced`` and ``max_abs_diff``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``n_unbalanced``: number of transactions with debits ≠ credits
- ``max_abs_diff``: largest absolute imbalance amount

TA line: “If max_abs_diff is nonzero, we have an integrity error.”

``accounting_equation_balances: True``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Total assets equal total liabilities plus equity (system-wide sanity check).

TA line: “Even if each transaction balances, you still want the big equation to hold.”

7.2 Key metrics (how to interpret)
----------------------------------

Revenue and sales behavior
^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``sales_total``: total sales
- ``n_sales``: number of sales events
- ``avg_sale``: average sale size
- ``pct_sales_on_account``: fraction of sales made on credit

TA line: “A/R exists because not all sales are paid immediately. This hints at liquidity risk.”

Cost and margin
^^^^^^^^^^^^^^^

- ``cogs_total``: cost of goods sold
- ``gross_profit`` = sales − cogs
- ``gross_margin_pct`` = gross_profit / sales

TA line: “Gross margin is a core health metric and often a driver variable later.”

Net income and cash
^^^^^^^^^^^^^^^^^^^

- ``net_income`` may be negative
- ``ending_cash`` may still be positive

Teaching moment
^^^^^^^^^^^^^^^

“Profit and cash are not the same thing. You can lose money but still have cash (owner contributions, timing).
You can also earn profit and run out of cash.”

8. Outputs (what to open)
=========================

Outputs are written under:

- ``outputs/track_d/``

Students should open:

- ``outputs/track_d/d00_peek_data_summary.md`` (readable dataset inventory)
- Any CSV artifacts written by the runs (trial balance, statements, etc.)

TA line: “In real work, reproducible artifacts matter more than console output.”

9. Run the smoke tests (``business_smoke``)
===========================================

.. code-block:: bash

   pystatsv1 workbook check business_smoke

Students should see something like:

- “13 passed …”

Explain plainly
---------------

“These are automated checks that verify the workbook behaves as promised: commands run, outputs appear, and key
invariants stay true. Passing tests means your lab environment is healthy.”

10. Common issues and quick fixes
=================================

Command not found
-----------------

If ``pystatsv1`` isn’t recognized, use module form:

.. code-block:: bash

   python -m pystatsv1 workbook --help

Wrong folder
------------

If outputs/data can’t be found, confirm they’re inside the workbook folder:

.. code-block:: bash

   pwd
   ls

Reset everything
----------------

.. code-block:: bash

   pystatsv1 workbook run d00_setup_data --force
   pystatsv1 workbook run d00_peek_data

Confusion about negative income
-------------------------------

Teaching moment: owner contributions are cash inflows but not revenue.
Show them the contribution entry in ``gl_journal.csv`` and compare to sales lines.

11. Discussion prompts (if time)
================================

1. Why is ``pct_sales_on_account`` not zero? What does credit sales imply about cash planning?
2. Gross margin around ~45%: what types of businesses might fit?
3. Net income negative but cash positive: what events create that pattern?
4. NSO includes a deliberate duplicate bank transaction ID: why include intentional errors?

12. Closing script (30 seconds)
===============================

“Today you proved you can set up a reproducible environment, inspect accounting-style datasets, validate integrity
constraints, and generate a first business summary. That’s the workflow: make data trustworthy before analyzing it.
Next labs build on this foundation toward statistical reasoning and decision support.”


Track D Lab + TA Notes (PyPI-only)
==================================

.. tip::

   If students are new to the Track D case, have them read :doc:`track_d_student_edition` first.


Appendix A: Command block (TA slide)
====================================

.. code-block:: bash

   # Setup (once)
   python -m venv .venv
   source .venv/Scripts/activate
   python -m pip install -U pip
   pip install "pystatsv1[workbook]"

   # Start Track D
   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

   # Tour + first checks
   pystatsv1 workbook list --track d
   pystatsv1 workbook run d00_peek_data
   pystatsv1 workbook run d01

   # Confidence check
   pystatsv1 workbook check business_smoke
