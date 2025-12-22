Business Chapter 6: Reconciliations as Quality Control
======================================================

Chapter 6 treats reconciliations as a **quality control system** for bookkeeping and data pipelines.

A reconciliation is a comparison between two independent sources of truth. In practice, it answers questions like:

- Do my subledgers agree with the general ledger and trial balance?
- Do my cash transactions in the GL agree with what the bank says happened?
- If they disagree, can I produce an **exception report** that tells me what to fix?

In the NSO running case we implement two classic reconciliations:

1. **Accounts receivable (A/R) roll-forward** (subledger → trial balance tie-out)
2. **Bank reconciliation** (bank statement → GL cash activity match + exceptions)

What you should be able to do after this chapter
------------------------------------------------

Accounting concepts
^^^^^^^^^^^^^^^^^^
- Explain why reconciliations are a core internal control (and why auditors care).
- Build an A/R roll-forward and interpret a tie-out difference.
- Categorize bank recon exceptions (missing GL, missing bank line, duplicates, timing differences).

Python / software concepts
^^^^^^^^^^^^^^^^^^^^^^^^^^
- Implement a matching procedure and produce both “matches” and “exceptions” tables.
- Store summary results as machine-readable JSON (useful for CI dashboards).
- Use deterministic anomaly injection (in the simulator) to ensure tests cover edge cases.

Inputs and outputs
------------------

Inputs (NSO v1 dataset folder)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Chapter 6 uses:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Table
     - Purpose
   * - ``gl_journal.csv``
     - General ledger journal lines (we use it to reconstruct cash transactions for reconciliation).
   * - ``trial_balance_monthly.csv``
     - Control totals (A/R ending balances).
   * - ``ar_events.csv``
     - A/R subledger events (invoices and collections) with an explicit ``ar_delta``.
   * - ``bank_statement.csv``
     - Bank statement feed (external truth) with ``bank_txn_id`` and optional link to ``gl_txn_id``.

Outputs (``outdir``)
^^^^^^^^^^^^^^^^^^^^
The Chapter 6 script writes:

- ``ar_rollforward.csv`` — monthly A/R roll-forward with a tie-out ``diff`` column.
- ``bank_recon_matches.csv`` — bank lines and whether they matched to a GL cash transaction.
- ``bank_recon_exceptions.csv`` — unmatched items with an ``exception_type`` label.
- ``ch06_summary.json`` — check flags + metrics + exception counts.

Where these tables come from in code
------------------------------------

- Simulator additions (Chapter 6 tables): :mod:`scripts.sim_business_nso_v1`
- Chapter 6 helpers (matching + roll-forward): :mod:`scripts._business_recon`
- Chapter 6 analysis script: :mod:`scripts.business_ch06_reconciliations_quality_control`

Running the chapter
-------------------

.. code-block:: bash

   make business-nso-sim
   make business-ch06

Or:

.. code-block:: bash

   python -m scripts.business_ch06_reconciliations_quality_control      --datadir data/synthetic/nso_v1      --outdir outputs/track_d      --seed 123

A/R roll-forward tie-out
------------------------

The A/R roll-forward uses a standard pattern:

.. math::

   \text{Ending A/R} = \text{Beginning A/R} + \text{Invoices} - \text{Collections}

In the dataset, ``ar_events.csv`` provides an explicit ``ar_delta`` for each event.
The chapter script aggregates by month and compares the computed ending A/R to the A/R account balance in the trial balance.
The output includes a ``diff`` column:

- ``diff = computed_ending_ar - trial_balance_ar``

A non-zero diff is your cue to investigate: missing events, wrong sign conventions, or wrong account mapping.

Bank reconciliation
-------------------

What we match
^^^^^^^^^^^^^
A bank statement is external evidence of cash movement. The GL is the internal record of cash movement.
A reconciliation tries to match these two.

In this project we:

1. Extract **cash-related transactions** from the GL (by cash account id).
2. Use the bank statement feed as the “bank side”.
3. Match by transaction id / link when available, and otherwise fall back to rules (amount, date window, description).

Why we inject anomalies
^^^^^^^^^^^^^^^^^^^^^^^
The simulator intentionally injects a small number of deterministic anomalies (for example, a bank fee with no GL link)
so that:

- the reconciliation produces a non-empty exception report, and
- unit tests can assert the exception categories are handled.

Reading the summary JSON
------------------------

Open ``outputs/track_d/ch06_summary.json`` after running the chapter. It contains:

- ``checks``: boolean pass/fail flags (e.g., A/R ties to the trial balance)
- ``metrics``: counts of bank lines, cash txns, matches, exceptions
- ``exception_counts``: a breakdown by exception type

Exercises and extensions
------------------------

1. Add a new anomaly type (e.g., “timing difference”) and update the matching rules + tests.
2. Change the match tolerance (date window) and observe how the exception counts change.
3. Extend the reconciliation to produce a “reconciling items” roll-forward that bridges bank cash to book cash.

Notes for maintainers
---------------------

- Reconciliations are extremely testable. When you add a new exception type,
  add a deterministic injected case in the simulator and assert it appears in ``bank_recon_exceptions.csv``.
- Keep the chapter script small and narrative; move reusable reconciliation logic into :mod:`scripts._business_recon`.
