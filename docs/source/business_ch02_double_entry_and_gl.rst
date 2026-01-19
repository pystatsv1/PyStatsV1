.. _business-ch02:

Ch 02 — Double-entry and the general ledger as a database
=========================================================

.. |trackd_run| replace:: d02
.. include:: _includes/track_d_run_strip.rst


Why this matters (for accountants)
----------------------------------
Your general ledger (GL) is a *database of business events*. If it’s structured well
(and posted consistently), analysis becomes fast, reliable, and repeatable — and
forecasting later becomes dramatically easier.

This chapter translates “debits and credits” into a data model:
rows, keys, validation rules, and tidy exports.

Learning objectives
-------------------
- Explain debits and credits in plain language (double-entry logic).
- Interpret the chart of accounts (COA) as an analytics schema.
- Produce an analysis-ready GL export with signed amounts and statement mapping.
- Run controls-aware checks that catch common posting errors early.

Concise refresher: double-entry and the GL (RTD-native)
-------------------------------------------------------
**Double-entry accounting** means every business event is recorded with equal total
debits and total credits. This is a built-in *consistency check* that helps you catch
errors early and supports a clean audit trail.

**Debits and credits** are not “good vs bad.” They are *directional signs* that depend
on the *type of account*:

- **Assets** normally carry a **debit** balance (cash, inventory, equipment).
- **Liabilities** normally carry a **credit** balance (accounts payable, loans).
- **Equity** normally carries a **credit** balance (owner’s equity, retained earnings).
- **Revenue** normally carries a **credit** balance (sales).
- **Expenses** normally carry a **debit** balance (rent, payroll expense).

A single transaction is typically stored as **multiple GL lines** that share a common
transaction identifier (``txn_id``). Example (cash sale):

- Debit Cash
- Credit Sales Revenue

If you later discover an error, best practice is to **correct with a new entry**
(or a reversing entry + replacement) rather than deleting history.

**Chart of Accounts (COA)** is your ledger’s *schema*: it defines accounts, rollups,
and stable reporting structure.

**Trial Balance (TB)** is the monthly “checksum”: it summarizes debits/credits by account
and helps you confirm internal consistency before producing financial statements.

Common posting errors and the control that catches them
-------------------------------------------------------
These are the problems that silently destroy analytics (and later, forecasts) —
and the simplest control to prevent them:

1. **Unbalanced transactions** (debits ≠ credits)
   - Control: per-``txn_id`` balancing check; block posting or flag for review.

2. **Wrong account selection / miscoding**
   - Control: COA governance (clear names, fewer ambiguous buckets) + variance review.

3. **Wrong period (cutoff errors)**
   - Control: month-end cutoff checklist; review large late entries.

4. **Swapped debit/credit direction**
   - Control: “normal balance” logic + automated reasonableness checks.

5. **Duplicate postings**
   - Control: duplicate detection on (date, amount, counterparty, doc_id) patterns.

In this chapter’s lab, we encode several of these as automated checks.

Accounting Connection (PDF refresher)
-------------------------------------
Refreshes: **double-entry**, **general ledger**, **bookkeeper role**.

Dataset tables used (LedgerLab core)
------------------------------------
This chapter continues with the small LedgerLab **core ledger** dataset.
The larger **NSO v1** running case (``data/synthetic/nso_v1``) is introduced in later chapters.

- ``chart_of_accounts.csv`` (COA “schema”: account_id, type, normal side)
- ``gl_journal.csv`` (transaction detail lines: debits, credits, doc IDs)
- ``trial_balance_monthly.csv`` (monthly checksum summary)

PyStatsV1 lab (Run it)
----------------------
If you haven’t generated the LedgerLab *core* dataset yet::

   make business-sim

Run Chapter 2::

   make business-ch02

Key artifacts written to ``outputs/track_d``:

- ``business_ch02_summary.json`` (checks + quick metrics)
- ``business_ch02_gl_tidy.csv`` (analysis-ready export: signed amounts + mapping)
- ``business_ch02_trial_balance.csv`` (recomputed from the GL)
- ``business_ch02_account_rollup.csv`` (rollup by account type)
- ``business_ch02_tb_by_account.png`` (plot)

What the automated checks verify (exactly)
------------------------------------------
When you run ``make business-ch02``, the script prints these checks:

Chart of Accounts (COA) checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``coa_account_ids_unique``: each ``account_id`` appears exactly once (a true schema).
- ``coa_account_types_valid``: account types are restricted to
  Asset, Liability, Equity, Revenue, Expense.
  (See also: ``coa_bad_account_types`` if anything is invalid.)
- ``coa_normal_sides_valid``: normal sides are only Debit or Credit.
  (See also: ``coa_bad_normal_sides`` if anything is invalid.)

GL integrity checks
^^^^^^^^^^^^^^^^^^^
- ``gl_account_ids_in_coa``: every GL ``account_id`` exists in the COA.
  (See also: ``gl_missing_account_ids`` to list offenders.)
- ``gl_debits_nonnegative`` and ``gl_credits_nonnegative``: prevents negative postings
  that usually indicate sign mistakes or malformed exports.

Double-entry transaction check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``transactions_balanced``: for every ``txn_id``, sum(debits) == sum(credits).
  Companion diagnostics:
  - ``n_transactions``: number of transactions observed
  - ``n_unbalanced``: number of transactions failing the rule
  - ``max_abs_diff``: worst imbalance magnitude (0.0 is ideal)

Trial balance tie-out
^^^^^^^^^^^^^^^^^^^^^
- ``trial_balance_matches_source``: trial balance recomputed from detail GL lines matches
  the provided ``trial_balance_monthly.csv``.
  - ``trial_balance_max_abs_diff``: largest absolute difference (floating-point noise
    close to 0 is normal).

Interpretation & decision memo
------------------------------
- What GL structure decisions help forecasting later?
  (stable account definitions, consistent dimensions, clear statement mapping)
- What controls prevent miscoding and reclass churn?
  (transaction balancing, COA governance, tie-outs, cutoff discipline)

End-of-chapter problems
-----------------------
1. Post a set of transactions; verify debits=credits by transaction ID.
2. Redesign a messy COA into an analysis-friendly COA (fewer ambiguous buckets).
3. Propose a month-end checklist that prevents recurring coding errors.
4. Define your signed-amount convention and explain how it affects reporting.

Textbook alignment notes
------------------------
Textbook Part A: Chapters 1–3.
