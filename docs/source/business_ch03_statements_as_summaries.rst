.. _business-ch03:

Ch 03 — Financial statements as summary statistics
==================================================

Why this matters (for accountants)
----------------------------------
Financial statements are *aggregated views of the ledger*.
They are “summary statistics” for business performance and position.

But like any summary:
- they are only as good as the underlying ledger structure and posting discipline, and
- they can hide important drivers (timing, classification, and working-capital effects).

Forecasting starts by understanding what these summaries do (and do not) tell you.

Learning objectives
-------------------
By the end of this chapter, you will be able to:

1. Connect journal → trial balance → statements as a reproducible pipeline.
2. Explain the links among the income statement (P&L), balance sheet, and cash flow.
3. Translate statement lines into operational drivers (sales volume, margins, working capital).
4. Run controls-aware reconciliation checks so statement analytics are trustworthy.

Core terms (fast refresher)
---------------------------

Income statement (P&L)
^^^^^^^^^^^^^^^^^^^^^^
The income statement summarizes performance over a period:

- **Revenue** (value earned)
- **Expenses** (resources consumed)
- **Net income** = revenue − expenses

Key idea: P&L is *flow over time* (a period summary), not a point-in-time snapshot.

Balance sheet
^^^^^^^^^^^^^
The balance sheet summarizes position at a point in time:

.. math::

   \text{Assets} = \text{Liabilities} + \text{Equity}

Key idea: the balance sheet is a *snapshot* (end-of-period totals).

Cash flow statement
^^^^^^^^^^^^^^^^^^^
The cash flow statement explains why cash changed:

- **Cash from operations**: cash impact of core business activity
- **Cash from investing**: long-term asset purchases/sales
- **Cash from financing**: owner contributions, loans, repayments, distributions

Key idea: the cash flow statement is the “bridge” between net income and cash change.

Why net income ≠ cash change (the big refresher idea)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Net income differs from cash change mainly because of:

1. **Accrual timing** (earned/incurred vs paid)
2. **Working capital changes** (AR, inventory, AP)
3. **Financing and investing flows** (cash changes that are not “income”)

Accounting Connection (PDF refresher)
-------------------------------------
Refreshes: **income statement**, **balance sheet**, **cash flows**.

Dataset tables used (LedgerLab)
-------------------------------
- ``chart_of_accounts.csv``
- ``gl_journal.csv``
- ``trial_balance_monthly.csv``
- ``statements_is_monthly.csv``
- ``statements_bs_monthly.csv``
- ``statements_cf_monthly.csv``

PyStatsV1 lab (Run it)
----------------------
If you haven’t generated LedgerLab yet::

   make business-sim

Run Chapter 3::

   make business-ch03

Key artifacts written to ``outputs/track_d``:

- ``business_ch03_summary.json`` (checks + key metrics)
- ``business_ch03_statement_bridge.csv`` (net income → cash change bridge)
- ``business_ch03_trial_balance.csv`` (recomputed from the GL)
- ``business_ch03_net_income_vs_cash_change.png`` (plot)

What the automated checks verify (exactly)
------------------------------------------
When you run ``make business-ch03``, the script prints a controls-style checklist.
These are intentionally “audit-friendly”: they tell you whether the summaries reconcile.

Ledger integrity checks
^^^^^^^^^^^^^^^^^^^^^^^
- ``transactions_balanced``: for every ``txn_id``, sum(debits) == sum(credits).
  Companion diagnostics:
  - ``n_transactions``
  - ``n_unbalanced``
  - ``max_abs_diff``

Trial balance reconciliation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``trial_balance_matches_source``: recomputed TB (from the GL) matches ``trial_balance_monthly.csv``.
  Companion diagnostic:
  - ``trial_balance_max_abs_diff``

Statement reconciliation
^^^^^^^^^^^^^^^^^^^^^^^^
- ``income_statement_ties_to_trial_balance``: statement revenue/expense/net income agrees with TB-derived totals.
  Companion diagnostic:
  - ``income_statement_max_abs_diff``

- ``balance_sheet_equation_balances``: verifies assets = liabilities + equity.
  Companion diagnostic:
  - ``balance_sheet_abs_diff``

Cash flow tie-out
^^^^^^^^^^^^^^^^^
- ``cash_flow_ties_to_balance_sheet_cash``: ending cash from the cash flow bridge matches the balance sheet cash line.
  Companion diagnostic:
  - ``cash_flow_cash_abs_diff``

Small nonzero differences extremely close to 0 can occur due to floating-point arithmetic;
treat anything near machine precision as “effectively zero.”

Interpretation & decision memo
------------------------------
After you run the lab, answer these prompts in 6–10 sentences:

1. Why does net income differ from the change in cash in this month?
2. Which statement lines look like “drivers” (inputs you can influence) vs “outcomes”?
3. If you had to forecast one line next month, which would it be and why?
4. What control(s) would you add if these were real books?

End-of-chapter problems
-----------------------
1. Explain three reasons net income differs from cash change (use AR/inventory/AP examples).
2. Map GL accounts to statement lines and justify your mapping rules.
3. Define 5 KPIs tied to statement lines (include formulas).
4. Propose a “close checklist” that prevents timing and classification errors.

Textbook alignment notes
------------------------
Textbook Part A: Chapters 1–3.
