Business Chapter 5: Liabilities — Payroll, Taxes, Debt, and Equity
==================================================================

.. |trackd_run| replace:: d05
.. include:: _includes/track_d_run_strip.rst


This chapter expands the running case from “assets” to the other side of the accounting equation:

.. math::

   \textbf{Assets} = \textbf{Liabilities} + \textbf{Equity}

Liabilities and equity are where bookkeeping becomes *timing‑sensitive*:
you record obligations when they are incurred (accrual basis), and later you clear them when cash moves.

Chapter 5 introduces several common subledgers that are perfect examples of **governed datasets**:

- Payroll payables (wages payable, payroll taxes payable)
- Sales tax payable (tax collected on taxable sales)
- Accounts payable (vendor invoices and payments)
- Notes payable (loan balance roll-forward with interest vs principal)
- Equity events (contributions / distributions)

What you should be able to do after this chapter
------------------------------------------------

Accounting concepts
^^^^^^^^^^^^^^^^^^^
- Explain what it means for an obligation to be **incurred** vs **paid**.
- Build a monthly **roll-forward** (beginning balance + changes = ending balance).
- Distinguish **interest expense** from **principal repayment** in a loan payment.
- Describe how equity changes through owner contributions and distributions.

Python / software concepts
^^^^^^^^^^^^^^^^^^^^^^^^^^
- Model subledger events as tidy tables and aggregate them to produce roll-forwards.
- Implement validation checks that tie subledgers to control totals (trial balance).
- Produce stable, inspectable artifacts (CSV + JSON) that work in CI and in documentation.

Inputs and outputs
------------------

Inputs (NSO v1 dataset folder)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Chapter 5 uses the monthly trial balance plus five subledger tables produced by the simulator:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Table
     - Purpose
   * - ``trial_balance_monthly.csv``
     - Control totals for payable / debt / equity accounts.
   * - ``payroll_events.csv``
     - Payroll event stream (gross wages, withholdings, employer taxes, cash paid, and payable deltas).
   * - ``sales_tax_events.csv``
     - Sales tax event stream (tax accrued, cash remitted, delta to sales tax payable).
   * - ``ap_events.csv``
     - Accounts payable events (vendor invoices, payments, and delta to A/P).
   * - ``debt_schedule.csv``
     - Amortization schedule per loan (beginning balance, payment, interest, principal, ending balance).
   * - ``equity_events.csv``
     - Owner contributions/distributions (simplified equity change events).

Outputs (``outdir``)
^^^^^^^^^^^^^^^^^^^^
The Chapter 5 script writes:

- ``business_ch05_summary.json`` — pass/fail checks and headline metrics.
- ``business_ch05_wages_payable_rollforward.csv`` — wages payable roll-forward.
- ``business_ch05_payroll_taxes_payable_rollforward.csv`` — payroll taxes payable roll-forward.
- ``business_ch05_sales_tax_payable_rollforward.csv`` — sales tax payable roll-forward.
- ``business_ch05_accounts_payable_rollforward.csv`` — accounts payable roll-forward.
- ``business_ch05_notes_payable_rollforward.csv`` — notes payable roll-forward (loan balance + interest/principal decomposition).
- ``business_ch05_liabilities_over_time.png`` — a quick visual showing key liabilities through time.

Where these tables come from in code
------------------------------------

- Simulator: :mod:`scripts.sim_business_nso_v1`
- Contracts: :mod:`scripts._business_schema`
- Chapter 5 analysis: :mod:`scripts.business_ch05_liabilities_payroll_taxes_equity`

Running the chapter
-------------------

.. code-block:: bash

   make business-nso-sim
   make business-ch05

Or:

.. code-block:: bash

   python -m scripts.business_ch05_liabilities_payroll_taxes_equity      --datadir data/synthetic/nso_v1      --outdir outputs/track_d      --seed 123

Roll-forwards as “data reconciliations”
---------------------------------------

A roll-forward is one of the most useful patterns in accounting *and* data engineering:

.. math::

   \text{Ending} = \text{Beginning} + \text{Increases} - \text{Decreases}

In this project, each subledger event table includes an explicit delta column
(e.g., ``ap_delta`` or ``sales_tax_payable_delta``). The chapter script aggregates these deltas by month and checks that:

- the computed ending balances match the trial balance for the corresponding accounts, and
- the cash portions align with cash activity in the GL when applicable.

Payroll payables (high level)
-----------------------------

Payroll is a bundle of related obligations:

- **Gross wages**: what employees earned.
- **Employee withholdings**: amounts withheld from paychecks (not an employer expense).
- **Employer payroll taxes**: employer-side taxes (an expense).
- **Wages payable / payroll taxes payable**: liabilities that may exist between the payroll date and payment date.

This chapter separates wages payable from payroll taxes payable so learners can see why payroll is not “just one number.”

Sales tax payable (high level)
------------------------------

Sales tax often behaves like a liability the business is collecting on behalf of a government:

- When a taxable sale occurs, the business records a liability (sales tax payable).
- When remitted, the liability decreases and cash decreases.

Accounts payable (high level)
-----------------------------

A/P tracks vendor invoices and payments:

- Recording an invoice increases A/P (liability).
- Paying the vendor decreases A/P and decreases cash.

Notes payable (high level)
--------------------------

Loan payments usually contain:

- **Interest** (expense) and
- **Principal** (reduces the liability).

The notes payable roll-forward output makes this decomposition explicit month-by-month.

Reading the outputs
-------------------

.. code-block:: python

   import pandas as pd

   ap = pd.read_csv("outputs/track_d/business_ch05_accounts_payable_rollforward.csv")
   notes = pd.read_csv("outputs/track_d/business_ch05_notes_payable_rollforward.csv")

   print(ap.tail())
   print(notes.tail())

Exercises and extensions
------------------------

1. Introduce a “late payment” scenario (shift cash paid to a later month) and verify how payables change.
2. Add a second loan with a different rate and term; compare interest profiles.
3. Extend the plot to include equity and show how liabilities and equity together finance assets.

Notes for maintainers
---------------------

- If you change any of the Chapter 5 tables (columns, names), update :mod:`scripts._business_schema`
  and add/adjust tests.
- The goal is not only to compute results, but to show learners the *audit trail*:
  event table → roll-forward → tie-out to trial balance.
