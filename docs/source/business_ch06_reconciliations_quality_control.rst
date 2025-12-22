Business Chapter 6
==================

Reconciliations as Quality Control
---------------------------------

Chapter 6 treats **reconciliations as data validation**.

In Chapters 1–5, you learned to record transactions and generate statements.
In real work, you also need confidence that the dataset is correct:

- Does the cash ledger agree to the bank statement?
- Does Accounts Receivable subledger activity reconcile to the AR control?

This chapter adds two dataset contract tables:

- ``ar_events.csv`` — AR subledger activity derived from GL postings to AR
- ``bank_statement.csv`` — external cash truth (with deterministic anomalies)

Artifacts
---------

The Chapter 6 script produces:

- ``ar_rollforward.csv`` — begin + activity = end vs trial balance
- ``bank_recon_matches.csv`` — bank lines matched to book cash txns
- ``bank_recon_exceptions.csv`` — typed exception report
- ``ch06_summary.json`` — checks + metrics

Run
---

.. code-block:: bash

   python -m scripts.business_ch06_reconciliations_quality_control \
       --datadir data/synthetic/nso_v1 \
       --outdir data/derived/business/ch06

Or via Makefile:

.. code-block:: bash

   make business-ch06

Teaching Notes
--------------

- Timing differences show up as unmatched items (bank-only or book-only).
- Error items show up as duplicates, sign issues, or amount mismatches.
- AR tie-outs emphasize control totals: the rollforward must match the TB control.
