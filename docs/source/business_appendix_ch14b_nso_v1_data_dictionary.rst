Appendix 14B: NSO v1 data dictionary cheat sheet (table → grain → keys → joins → checks)
======================================================================================

This appendix is a compact “reference page” for the **NSO v1 synthetic dataset** used across Track D
and specifically in Chapter 14.

Where this data lives
---------------------

NSO v1 is generated locally (and is gitignored):

- Default dataset folder: ``data/synthetic/nso_v1/``

Generate it with:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Tip: The most important idea is **lineage**.

- Subledgers and operational tables capture activity (A/R, A/P, inventory, payroll…).
- The GL journal captures double-entry truth.
- Monthly statements summarize the GL and are used for trend + driver analysis.


Core accounting tables (GL + statements)
----------------------------------------

.. list-table:: Core accounting tables
   :header-rows: 1
   :widths: 22 20 26 22 20

   * - Table
     - Grain (one row per…)
     - Key fields (high value columns)
     - Common joins
     - Common checks
   * - ``chart_of_accounts.csv``
     - Account (``account_id``)
     - ``account_id``, ``account_name``, ``account_type``, ``normal_side``
     - - ``account_id`` → ``gl_journal.account_id``
       - ``account_id`` → ``trial_balance_monthly.account_id``
     - - Unique ``account_id``
       - ``normal_side`` consistent with account type rules
   * - ``gl_journal.csv``
     - Journal line (``txn_id`` + ``account_id``)
     - ``txn_id``, ``date``, ``doc_id``, ``description``, ``account_id``, ``debit``, ``credit``
     - - ``account_id`` → COA
       - ``txn_id`` ↔ many event tables (A/R, A/P, inventory, payroll, tax, debt, equity)
       - ``txn_id`` ← ``bank_statement.gl_txn_id``
     - - For each ``txn_id``: sum(debit) == sum(credit)
       - ``debit``/``credit`` non-negative; one side usually zero
   * - ``trial_balance_monthly.csv``
     - Month × account (``month`` + ``account_id``)
     - ``month``, ``account_id``, ``debit``, ``credit``, ``ending_side``, ``ending_balance``
     - - ``account_id`` → COA
       - ``month`` → monthly statements (by month)
     - - For each month: total debits == total credits (sanity)
       - Ending balances stable vs GL-derived rebuild (when applicable)
   * - ``statements_is_monthly.csv``
     - Month × line (``month`` + ``line``)
     - ``month``, ``line``, ``amount`` (lines include Sales Revenue, COGS, Operating Expenses, Net Income)
     - - ``month`` → driver tables (e.g., Chapter 14)
       - ``month`` → cash flow bridge (by month)
     - - Gross Profit ≈ Revenue − COGS
       - Net Income ≈ Gross Profit − OpEx (for this synthetic model)
   * - ``statements_bs_monthly.csv``
     - Month × line (``month`` + ``line``)
     - ``month``, ``line``, ``amount`` (assets/liabilities/equity totals and key accounts)
     - - ``month`` → cash flow bridge
       - ``month`` → rollforwards (A/R, A/P, inventory, payables)
     - - Total Assets == Total Liabilities + Total Equity
       - Ending Cash agrees with cash flow “Ending Cash (from bridge)”
   * - ``statements_cf_monthly.csv``
     - Month × line (``month`` + ``line``)
     - ``month``, ``line``, ``amount`` (CFO/CFI/CFF bridge components + cash rollforward)
     - - ``month`` → BS and IS (by month)
     - - Ending Cash (from bridge) == Ending Cash (balance sheet)
       - Net Change in Cash == Ending − Beginning


Operational and subledger event tables
--------------------------------------

.. list-table:: Operational / subledger tables
   :header-rows: 1
   :widths: 22 20 26 22 20

   * - Table
     - Grain (one row per…)
     - Key fields
     - Common joins
     - Common checks
   * - ``inventory_movements.csv``
     - Inventory movement event (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``sku``, ``movement_type``, ``qty``, ``unit_cost``, ``amount``
     - - ``txn_id`` ↔ ``gl_journal.txn_id`` (inventory/COGS postings)
       - ``month`` → IS/BS (inventory + COGS by month)
     - - ``sale_issue`` qty sign convention consistent (units sold often computed as -sum(qty))
       - ``amount`` ≈ qty × unit_cost (within rounding rules)
   * - ``ar_events.csv``
     - A/R event (invoice or collection) (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``customer``, ``invoice_id``, ``event_type``, ``amount``, ``ar_delta``, ``cash_received``
     - - ``txn_id`` ↔ ``gl_journal.txn_id``
       - ``invoice_id`` ↔ ``gl_journal.doc_id`` (common pattern)
       - ``month`` → BS line “Accounts Receivable” (rollforward)
     - - Sum of ``ar_delta`` over time matches AR balance movement
       - Invoice vs collection behavior consistent (cash_received vs ar_delta)
   * - ``ap_events.csv``
     - A/P event (invoice or payment) (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``vendor``, ``invoice_id``, ``event_type``, ``amount``, ``ap_delta``, ``cash_paid``
     - - ``txn_id`` ↔ ``gl_journal.txn_id``
       - ``invoice_id`` ↔ ``gl_journal.doc_id`` (common pattern)
       - ``month`` → BS line “Accounts Payable” (rollforward)
     - - Sum of ``ap_delta`` over time matches AP balance movement
       - Payment rows show cash_paid behavior consistent with ap_delta
   * - ``payroll_events.csv``
     - Payroll event (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``event_type``, ``gross_wages``, ``employee_withholding``, ``employer_tax``, ``cash_paid``
     - - ``txn_id`` ↔ ``gl_journal.txn_id``
       - ``month`` → BS lines “Wages Payable” and “Payroll Taxes Payable”
     - - Payables deltas reconcile with BS payables lines
       - Cash paid timing consistent with accrual/payment/remittance cycle
   * - ``sales_tax_events.csv``
     - Sales tax event (collection or remittance) (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``event_type``, ``taxable_sales``, ``tax_amount``, ``cash_paid``
     - - ``txn_id`` ↔ ``gl_journal.txn_id``
       - ``month`` → BS line “Sales Tax Payable”
     - - Payable deltas reconcile with BS sales tax payable
       - Remittance reduces payable; collection increases payable
   * - ``bank_statement.csv``
     - Bank transaction (``bank_txn_id``)
     - ``month``, ``bank_txn_id``, ``posted_date``, ``description``, ``amount``, ``gl_txn_id``
     - - ``gl_txn_id`` → ``gl_journal.txn_id`` (link bank item to GL posting)
       - ``month`` → cash rollforward checks
     - - Bank items link to GL (gl_txn_id exists)
       - Aggregate cash activity consistent with CF/BS cash movement (in this synthetic model)


Schedules and supporting tables
-------------------------------

.. list-table:: Schedules / supporting tables
   :header-rows: 1
   :widths: 22 20 26 22 20

   * - Table
     - Grain (one row per…)
     - Key fields
     - Common joins
     - Common checks
   * - ``fixed_assets.csv``
     - Asset (``asset_id``)
     - ``asset_id``, ``asset_name``, ``in_service_month``, ``cost``, ``useful_life_months``, ``salvage_value``, ``method``
     - - ``asset_id`` → ``depreciation_schedule.asset_id``
       - ``in_service_month`` → depreciation start month logic
     - - Unique ``asset_id``
       - Life and salvage values sane (non-negative)
   * - ``depreciation_schedule.csv``
     - Asset × month (``asset_id`` + ``month``)
     - ``month``, ``asset_id``, ``dep_expense``, ``accum_dep``, ``net_book_value``
     - - ``asset_id`` → fixed_assets
       - ``month`` → IS/BS (Depreciation expense / Accumulated depreciation / Net PP&E)
     - - ``net_book_value`` decreases logically; never below salvage (for model rules)
       - Accumulated depreciation monotone increasing
   * - ``debt_schedule.csv``
     - Loan × month (``loan_id`` + ``month``)
     - ``month``, ``loan_id``, ``txn_id``, ``beginning_balance``, ``payment``, ``interest``, ``principal``, ``ending_balance``
     - - ``txn_id`` ↔ ``gl_journal.txn_id`` (debt-related postings)
       - ``month`` → BS line “Notes Payable” and CF financing section
     - - Beginning + principal logic consistent: ending ≈ beginning − principal (within rounding)
       - Payment ≈ interest + principal (within rounding)
   * - ``equity_events.csv``
     - Equity event (``txn_id``)
     - ``month``, ``txn_id``, ``date``, ``event_type``, ``amount``
     - - ``txn_id`` ↔ ``gl_journal.txn_id``
       - ``month`` → BS equity lines and CF (owner contribution/draw)
     - - Contribution increases equity; draw decreases equity (by sign convention)
   * - ``nso_v1_meta.json``
     - Dataset metadata (single document)
     - Seed, date window, scenario notes
     - - Not joined; used for reproducibility and audit trail
     - - Record seed/month window; keep alongside analyses for “what data was this?” tracking


Quick join patterns (most common in Track D)
--------------------------------------------

These are the joins you will use constantly:

.. code-block:: text

   gl_journal.account_id  -> chart_of_accounts.account_id
   trial_balance_monthly.account_id -> chart_of_accounts.account_id

   ar_events.txn_id       -> gl_journal.txn_id
   ap_events.txn_id       -> gl_journal.txn_id
   inventory_movements.txn_id -> gl_journal.txn_id
   payroll_events.txn_id  -> gl_journal.txn_id
   sales_tax_events.txn_id -> gl_journal.txn_id
   debt_schedule.txn_id   -> gl_journal.txn_id
   equity_events.txn_id   -> gl_journal.txn_id
   bank_statement.gl_txn_id -> gl_journal.txn_id

   (Monthly alignment)
   month -> statements_is_monthly.month / statements_bs_monthly.month / statements_cf_monthly.month


Quick “trust gates” (common checks you should do first)
-------------------------------------------------------

If you only have time for a few checks, do these:

1) **GL transactions balance**
   - For each ``txn_id`` in ``gl_journal.csv``: sum(debit) == sum(credit)

2) **Balance sheet equation holds**
   - In ``statements_bs_monthly.csv``: Total Assets == Total Liabilities + Total Equity

3) **Cash rollforward agrees**
   - In ``statements_cf_monthly.csv``: Ending Cash (from bridge) == Ending Cash (balance sheet)

4) **Subledger rollforward sanity**
   - AR/AP payables deltas move in the same direction as the corresponding BS lines.

These checks are why Track D can safely build “explainable regression” on top of the dataset:
we’re not modeling noise from broken measurement.
