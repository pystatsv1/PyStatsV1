Track D — Chapter 5
===================

Liabilities, payroll, taxes, and equity: obligations and structure
-----------------------------------------------------------------

This chapter is about *structure* and *controls-aware accounting mechanics*:

- Liabilities are not just “numbers on a balance sheet” — they represent obligations
  that must be tracked, paid, and reconciled.
- Payroll and sales tax are *compliance-heavy* flows where control failures show up
  quickly (penalties, notices, cash surprises).
- Debt introduces the most common classification trap: **principal vs interest**.
- Equity is the ownership “claim” and the bridge between operations (retained earnings)
  and financing (contributions/distributions).

In this repo, we treat these ideas the same way we treat statistics later:
**as data generating processes + validation checks**.

Learning objectives (from the outline)
--------------------------------------

By the end of this chapter you should be able to:

- Explain the defining features of a liability and classify common examples.
- Post AP, debt payments (principal vs interest), and payroll liabilities.
- Explain equity movements (contributions, distributions, retained earnings).
- Identify compliance/control checkpoints for payroll and sales tax.

Running case dataset: NSO v1 (multi-month)
------------------------------------------

Chapter 5 uses the NSO v1 running case (multi-month) produced by the simulator:

.. code-block:: bash

   make business-nso-sim

The simulator writes to:

``data/synthetic/nso_v1/``

Core tables
~~~~~~~~~~~

- ``chart_of_accounts.csv``
- ``gl_journal.csv``
- ``trial_balance_monthly.csv``
- ``statements_is_monthly.csv``
- ``statements_bs_monthly.csv``
- ``statements_cf_monthly.csv``

Ch04 tables (assets)
~~~~~~~~~~~~~~~~~~~~

- ``inventory_movements.csv``
- ``fixed_assets.csv``
- ``depreciation_schedule.csv``

Ch05 tables (obligations and structure)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are intentionally small and readable “mini-ledgers” / event logs:

- ``payroll_events.csv``

  Columns:

  - ``month`` (YYYY-MM)
  - ``txn_id``, ``date``
  - ``event_type`` ∈ {``payroll_run``, ``wage_accrual``, ``wage_payment``, ``tax_remittance``}
  - ``gross_wages``, ``employee_withholding``, ``employer_tax``
  - ``cash_paid``
  - ``wages_payable_delta`` (positive increases liability)
  - ``payroll_taxes_payable_delta`` (positive increases liability)

- ``sales_tax_events.csv``

  Columns:

  - ``month`` (YYYY-MM)
  - ``txn_id``, ``date``
  - ``event_type`` ∈ {``tax_collected``, ``tax_remittance``}
  - ``taxable_sales``, ``tax_amount``
  - ``cash_paid``
  - ``sales_tax_payable_delta``

- ``debt_schedule.csv``

  Columns:

  - ``month`` (YYYY-MM)
  - ``loan_id``, ``txn_id``
  - ``beginning_balance``, ``payment``, ``interest``, ``principal``, ``ending_balance``

- ``equity_events.csv``

  Columns:

  - ``month`` (YYYY-MM)
  - ``txn_id``, ``date``
  - ``event_type`` ∈ {``contribution``, ``draw``}
  - ``amount``

- ``ap_events.csv``

  Columns:

  - ``month`` (YYYY-MM)
  - ``txn_id``, ``date``, ``vendor``, ``invoice_id``
  - ``event_type`` ∈ {``invoice``, ``payment``}
  - ``amount``
  - ``ap_delta`` (positive increases AP)
  - ``cash_paid``

Why this design?
----------------

The book’s Part B later frames reconciliations as “data validation.”
We start that mindset here:

- Each event table is a **controlled source of truth** for a specific obligation stream.
- The GL is the **system of record**.
- Chapter scripts prove that the obligation subledger ties to the GL by construction
  using rollforwards and monthly totals.

Concept refresher
-----------------

What makes something a liability?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A liability is an obligation arising from past events that will require a future
outflow of resources.

Common classifications:

- Current vs non-current (timing matters for liquidity and forecasting)
- Operating liabilities (AP, wages payable, tax payable) vs financing (debt)
- Known vs estimated (accruals, provisions)

Principal vs interest (debt payments)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A debt payment is not “an expense.”

- **Interest** is the cost of borrowing → Income Statement expense.
- **Principal** is repayment of the balance → reduces the liability on the Balance Sheet.
- Cash decreases by the full payment.

Payroll (gross, deductions, employer portions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Payroll introduces multiple flows:

- Gross wages: expense
- Deductions/withholdings: liability (you owe the government / third parties)
- Employer payroll taxes: additional expense
- Remittances: cash outflow that reduces the liability

Sales tax (collection and remittance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sales tax is typically not revenue:

- When collected, it increases cash/AR and increases a liability.
- When remitted, it reduces cash and reduces the liability.

Equity movements
~~~~~~~~~~~~~~~~

Equity changes via:

- Owner contribution (financing inflow)
- Owner draw/distribution (financing outflow)
- Retained earnings (accumulated net income minus dividends/draws, depending on entity)

Automated checks performed by the Chapter 5 script
--------------------------------------------------

Run:

.. code-block:: bash

   make business-ch05

The script writes outputs to:

``outputs/track_d/``

Tie-out checks:

- Debt schedule ↔ GL:

  - Interest expense ties to GL interest expense account.
  - Notes payable rollforward ties to TB ending balances.

- Payroll events ↔ GL:

  - Payroll expense ties to GL payroll expense.
  - Employer payroll tax expense ties to GL payroll tax expense.
  - Wages payable rollforward ties to TB ending balances.
  - Payroll taxes payable rollforward ties to TB ending balances.

- Sales tax events ↔ GL:

  - Sales tax payable rollforward ties to TB ending balances.

- AP events ↔ GL:

  - Accounts payable rollforward ties to TB ending balances.

- Equity events ↔ GL:

  - Contributions tie to owner capital postings.
  - Draws tie to owner draw postings.

Outputs produced:

- ``business_ch05_summary.json``
- rollforward CSVs for each obligation stream
- ``business_ch05_liabilities_over_time.png``

How to think about the end-of-chapter problems
----------------------------------------------

1) Loan payment entry
~~~~~~~~~~~~~~~~~~~~~

Given a payment amount and an interest calculation:

- Record interest expense
- Record principal reduction
- Record cash decrease

Then describe impacts:

- IS: interest expense reduces net income
- BS: notes payable decreases (principal), cash decreases (full)
- CF: operating cash outflow for interest, financing for principal (conceptually)

2) Payroll mini-ledger
~~~~~~~~~~~~~~~~~~~~~~

Record:

- Gross pay
- Deductions
- Employer portion
- Remittances

Then confirm:

- liabilities move correctly over time
- remittance clears the liability stream

3) Equity rollforward
~~~~~~~~~~~~~~~~~~~~~

Given events:

- start equity
- add contributions
- subtract draws
- add net income (retained earnings concept)

Compute ending equity and tie to the Balance Sheet.

Next chapter
------------

Chapter 6 will formalize “controls as data validation”:

- Bank reconciliation (timing vs error)
- AR/AP ties
- exception reports

Chapter 5 is the foundation because it gives you realistic obligation streams
that will *require* reconciliation later.
