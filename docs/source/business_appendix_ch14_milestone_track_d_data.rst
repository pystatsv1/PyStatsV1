Appendix 14A: Chapter 14 milestone — Track D, the NSO system, and our synthetic datasets
======================================================================================

Chapter 14 is a milestone in Track D.

Up through Chapter 13, we focused on *measurement and inference*:
clean accounting structure, analysis-ready tables, descriptive statistics, probability,
sampling, hypothesis testing, and controlled comparisons.

In Chapter 14, we shift into *explanation for planning*:
**driver analysis** — a simple, auditable way to translate operational activity into
a quantitative story that accounting and operations can actually use.

This appendix is the “big picture + under the hood” companion to Chapter 14:

- What Track D is building (and why this is designed for accountants).
- Where our data comes from (synthetic datasets generated locally).
- What’s in the NSO running-case dataset and how it ties to chapters.
- How to regenerate / modify datasets safely and reproducibly.
- What comes next after Chapter 14 (forecasting and planning).

If you want a shorter milestone / philosophy view earlier in Track D, see:
:doc:`business_appendix_ch08_milestone_big_picture`.


Why Track D looks the way it does
---------------------------------

Track D is designed around a practical accounting workflow:

1. **Close**: post events and summarize them correctly.
2. **Clean**: reconcile and validate so the numbers are trustworthy.
3. **Explain**: use statistics to understand variance and identify drivers.
4. **Forecast**: predict future months with explicit assumptions and error tracking.
5. **Decide**: turn outputs into a memo, a plan, and control checks.

Chapter 14 lives in Step 3 (“Explain”). It answers questions like:

- “Are COGS rising because we sold more units, because unit costs rose, or both?”
- “What’s the *expected* revenue level for a given units-sold and invoice count mix?”
- “If we change operational levers, how should the P&L respond — and by how much?”


A quick “what we’ve built so far” (Ch01–Ch14)
---------------------------------------------

Track D is intentionally cumulative — later chapters assume the reader trusts the data.

**Ch01–Ch03: accounting as measurement and summaries**

- Accounting equation and classification as a measurement system.
- Double-entry and the GL as a database.
- Statements as “summary statistics” (income statement, balance sheet, cash flow).

**Ch04–Ch06: real accounting structure + quality control**

- Assets and inventory/fixed assets (how operational events become numbers).
- Liabilities/payroll/taxes/equity (what “owed” means, and how it shows up).
- Reconciliations and QC: bank tie-outs, subledger checks, and “trust gates”.

**Ch07–Ch09: analysis workflow and reporting contract**

- Turn accounting exports into analysis-ready tables.
- Descriptive statistics for performance monitoring.
- Reporting style: what a good analysis deliverable looks like.

**Ch10–Ch13: risk + inference**

- Probability and risk framing.
- Sampling and estimation (audit/control mindset).
- Hypothesis testing for decisions.
- Correlation vs causation; controlled comparisons and guardrails.

**Ch14: regression driver analysis (this milestone)**

- A monthly driver table built from operational + accounting records.
- Explainable OLS models that connect operational levers to financial outcomes.
- Outputs designed for planning conversations (not “math for math’s sake”).


Where the data comes from (and why it’s synthetic)
--------------------------------------------------

Track D uses **generated (synthetic) datasets** for a simple reason:

- They’re safe to share (no confidential client data).
- They’re reproducible (same seed → same dataset).
- They’re “tie-out friendly” (subledgers link cleanly into the GL).
- They’re intentionally structured to support teaching:
  reconciliation checks, clean joins, realistic accounting relationships, and
  predictable artifacts that can be tested.

Important: our synthetic data is generated **locally** and is **gitignored**.

- Output folder: ``data/synthetic/``
- This folder is excluded in ``.gitignore`` so the repo stays small and clean.
- You generate the data with Make targets or direct CLI runs (examples below).

The two key ideas are:

- **The repo contains the generators** (simulators) and validators.
- **Your machine produces the dataset** you analyze, deterministically.


The NSO running case dataset (v1)
---------------------------------

The NSO dataset (“North Shore Outfitters”) is the Track D running case.
It’s designed to feel like a small business with realistic accounting subsystems:

- GL detail (journal-level “database” of financial events)
- Bank activity (reconciliation)
- A/R and A/P subledgers (invoice and bill flows)
- Inventory movements (units and COGS logic)
- Payroll events (wages and liabilities)
- Fixed assets + depreciation schedule
- Monthly financial statements for trend work

The simulator that produces this dataset is:

- ``scripts/sim_business_nso_v1.py``

The default Make target writes to:

- ``data/synthetic/nso_v1/``


NSO v1 file map (what each table represents)
--------------------------------------------

The simulator writes a set of CSVs that you can think of as “mini sub-systems”.
Below is a practical map of what they mean.

.. list-table:: NSO v1 dataset outputs (generated locally)
   :header-rows: 1
   :widths: 30 70

   * - File
     - What it is / why it exists
   * - ``chart_of_accounts.csv``
     - The schema of the GL: account IDs, names, normal balance. Used throughout Track D.
   * - ``gl_journal.csv``
     - Transaction-level double-entry journal lines (the “database”). Source of truth for tie-outs.
   * - ``trial_balance_monthly.csv``
     - Monthly account balances derived from GL; supports statement builds and control checks.
   * - ``statements_is_monthly.csv``
     - Monthly income statement (revenue, COGS, expenses). Feeds trend work + driver analysis.
   * - ``statements_bs_monthly.csv``
     - Monthly balance sheet summary. Supports ratios, solvency, and “does this reconcile?” checks.
   * - ``statements_cf_monthly.csv``
     - Simple cash flow bridge (CFO/CFI/CFF style). Supports cash reasoning and planning.
   * - ``inventory_movements.csv``
     - Operational inventory log (in/out). Key for units sold and COGS reasoning.
   * - ``fixed_assets.csv``
     - Asset register: acquisitions and metadata for depreciation logic.
   * - ``depreciation_schedule.csv``
     - Depreciation by asset / month; supports fixed cost behavior and statement logic.
   * - ``payroll_events.csv``
     - Payroll activity events: wages and related liabilities.
   * - ``sales_tax_events.csv``
     - Sales tax collected/remitted events; supports liability reasoning and cash flow realism.
   * - ``ap_events.csv``
     - Accounts payable events (bills, payments). Supports payables workflow + controls.
   * - ``ar_events.csv``
     - Accounts receivable events (invoices, receipts). Key for invoice counts and revenue logic.
   * - ``debt_schedule.csv``
     - Debt timeline: principal/interest structure for liabilities and planning.
   * - ``equity_events.csv``
     - Owner contributions/draws (equity flows).
   * - ``bank_statement.csv``
     - Bank-like activity log for reconciliation exercises and cash controls.
   * - ``nso_v1_meta.json``
     - Metadata for reproducibility (seed, months, and scenario notes).

Tip: if you ever ask “where did this number come from?”, the answer should be traceable
back to either a subledger event table or to ``gl_journal.csv``.


How Chapter 14 uses NSO v1 (driver table lineage)
-------------------------------------------------

Chapter 14 intentionally uses a *small, explainable* driver set — enough to teach the method
without turning it into a data engineering chapter.

The driver table is monthly and includes:

- ``units_sold``:
  derived from ``inventory_movements.csv`` using the sales outflow rows
  (the operational quantity driver for COGS and revenue).

- ``invoice_count``:
  derived from ``ar_events.csv`` using invoice rows
  (a proxy for “transaction volume” / customer activity).

- ``sales_revenue`` and ``cogs``:
  pulled from ``statements_is_monthly.csv``
  (financial outcomes already summarized through the accounting system).

This lineage is deliberate:

- The “driver” fields come from operational subledgers.
- The “outcome” fields come from financial statements.
- That separation mirrors real accounting analytics work:
  operations → accounting → analysis → planning conversation.


Regenerating the dataset (the standard workflow)
------------------------------------------------

From the repo root, the normal Track D flow is:

.. code-block:: bash

   # Generate NSO v1 synthetic dataset locally (gitignored)
   make business-nso-sim

   # Run dataset validation checks (schema + basic consistency checks)
   make business-validate

   # Run Chapter 14 analysis (build driver table, fit models, write artifacts)
   make business-ch14

You can also run the simulator directly:

.. code-block:: bash

   python -m scripts.sim_business_nso_v1 --outdir data/synthetic/nso_v1 --seed 123 --start-month 2025-01 --n-months 24

And you can validate directly:

.. code-block:: bash

   python -m scripts.business_validate_dataset --datadir data/synthetic/nso_v1


Regenerating without overwriting (recommended for experimentation)
------------------------------------------------------------------

When experimenting, don’t overwrite your “baseline” dataset.
Generate a new dataset folder and point chapter scripts at it.

Example:

.. code-block:: bash

   # Create a new scenario dataset
   python -m scripts.sim_business_nso_v1 --outdir data/synthetic/nso_v1_experiment --seed 999 --start-month 2025-01 --n-months 24

   # Validate the new dataset
   python -m scripts.business_validate_dataset --datadir data/synthetic/nso_v1_experiment

   # Run Chapter 14 on the new dataset (custom datadir)
   python -m scripts.business_ch14_regression_driver_analysis --datadir data/synthetic/nso_v1_experiment --outdir outputs/track_d --seed 123

If you prefer Make, you can override variables at runtime:

.. code-block:: bash

   make business-ch14 OUT_NSO_V1=data/synthetic/nso_v1_experiment

(That works because Make lets command-line variables override Makefile defaults.)


How to modify the synthetic datasets (what “modification” means here)
---------------------------------------------------------------------

There are two “levels” of modification, depending on your goal.

Level 1: change *generation knobs* (fast, safe)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are ideal for teaching, experimentation, and reproducibility:

- ``--seed``: changes the random realization of events while keeping structure consistent
- ``--start-month``: shifts the calendar window
- ``--n-months``: creates shorter/longer histories (useful for forecasting chapters later)

This level preserves the same schema and tends to keep downstream chapters stable.

Level 2: change *business story assumptions* (powerful, but do it deliberately)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is where you alter the simulated business behavior itself — for example:

- Different product mix or unit economics
- More/less volatility in demand
- Different payment terms (cash vs credit)
- More payroll headcount growth (step costs)
- Higher frequency of one-off shocks (supplier issues, returns, etc.)

These changes are educational gold — but they can also break assumptions in later chapters
if you change the “shape” of the data too aggressively.

When you do Level 2 changes, treat it like a controlled experiment:

1. Generate into a new outdir (don’t overwrite baseline)
2. Validate the dataset
3. Re-run the chapter(s) you care about
4. Compare artifacts and write down what changed (assumptions log)


Why this matters: regression needs stable measurement
-----------------------------------------------------

Regression driver analysis is only as credible as the measurement pipeline behind it.

That’s why Track D spends so much time on:

- classification and mapping (COA discipline),
- reconciliations (bank tie-outs),
- subledger consistency checks, and
- repeatable reporting artifacts.

If the dataset is “messy”, regression becomes a confidence trick:
coefficients look precise but reflect inconsistent measurement, not business reality.


What’s next after Chapter 14 (how this tees up Chapter 15+)
-----------------------------------------------------------

Chapter 14 is “explain the variance.”

Chapters 15+ move into “predict and plan”:

- Forecast hygiene: horizon, granularity, backtesting, and error metrics
- Forecast versioning: assumptions logs and change control
- Revenue forecasting: segmentation + drivers (not just a single trend line)
- Expense forecasting: fixed/variable/step cost behavior (payroll as a model)
- Communicating uncertainty: forecast ranges, risk flags, and decision memos

In other words:

- Ch14 turns drivers into explainable models.
- Ch15+ turns explainable models into **forecast workflows** that stand up to scrutiny.


Troubleshooting
---------------

**Problem: `make business-ch14` fails because files are missing**
- Cause: ``data/synthetic/nso_v1`` hasn’t been generated locally yet.
- Fix:

  .. code-block:: bash

     make business-nso-sim
     make business-validate
     make business-ch14


**Problem: Outputs go into `outputs/track_d/track_d`**
- Cause: Chapter 14’s CLI writes into ``--outdir`` plus a Track D subfolder for organization.
- Fix: This is expected. Treat ``outputs/track_d`` as your “project outputs root”.


**Problem: You edited the simulator and validation fails**
- Cause: You changed the business story or schema.
- Fix:
  1) regenerate into a new outdir,
  2) re-run validation,
  3) keep schema stable unless you intend to update multiple chapters.


Closing note
------------

This project is intentionally “controls-aware”:

- It teaches analytics that can be explained and audited.
- It respects accounting structure (not just data science convenience).
- It treats reproducibility and validation as non-negotiable.

Chapter 14 is the point where that philosophy becomes visible:
**drivers → model → explanation → planning conversation**.


- :doc:`business_appendix_ch14b_nso_v1_data_dictionary`

