.. |trackd_run| replace:: d19
.. include:: _includes/track_d_run_strip.rst

Track D — Chapter 19
====================

Cash flow forecasting (direct method, 13-week)
----------------------------------------------

A business can look profitable on the income statement and still run out of cash.
That is why many finance teams maintain a **short-term cash forecast** that is updated
frequently (weekly is common).

This chapter builds a **13-week cash forecast** using the **direct method**:

- **Receipts** (cash in): cash sales, customer collections, financing inflows
- **Payments** (cash out): vendors, payroll, taxes, debt payments, capex

The focus is accountant-friendly:

- Use the bank feed as the cash source of truth (timing matters).
- Explain changes in cash using AR/AP behaviour and payment policies.
- Stress test the forecast with conservative scenarios.

Learning objectives
-------------------

By the end of this chapter you will be able to:

- Build a short-term cash forecast with a clear horizon and update cadence.
- Separate cash flows into **receipts** and **payments** (direct method).
- Model working-capital timing using simple AR/AP assumptions.
- Define a cash buffer policy and **trigger thresholds** for action.

Data source (NSO v1)
--------------------

This chapter uses these simulator tables:

- ``bank_statement.csv`` — the timing of cash entering/leaving the bank
- ``ar_events.csv`` — invoices and collections (to explain collections timing)
- ``ap_events.csv`` — vendor invoices and payments (to explain payment behaviour)

We treat the bank statement as the primary cash truth and use the subledgers
to explain why cash moved.

Walkthrough (direct method)
---------------------------

1) Build weekly cash history
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We aggregate the bank statement into weekly totals:

- cash in total
- cash out total
- net cash flow (in - out)
- running cash balance

2) Build a 13-week baseline forecast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A practical baseline is “pattern + averages”:

- estimate typical weekly receipts and payments by category
- keep monthly items monthly (rent, many remittances)
- start the forecast from the **most recent actual cash balance**

3) Stress test and add a buffer policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We add two stress scenarios:

- **Delayed collections**: some customer payments arrive later than expected
- **Supplier terms tighten**: higher / faster payments to vendors

Then we define a simple cash buffer target (based on recent outflow volatility).
If projected cash falls below the buffer, the forecast flags a trigger for action.

How to run Chapter 19
---------------------

Prerequisite: generate the NSO dataset (once)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already ran Chapters 14–18, you already have NSO v1 in:

``data/synthetic/nso_v1``

If not:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Run the Chapter 19 analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-ch19

By default this runs:

.. code-block:: bash

   python -m scripts.business_ch19_cash_flow_forecasting_direct_method_13_week \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
-------

All artifacts are written under:

``outputs/track_d``

Core tables (CSV)
^^^^^^^^^^^^^^^^^

- ``ch19_cash_history_weekly.csv``
  Weekly cash history derived from ``bank_statement.csv``.

- ``ch19_cash_forecast_13w_scenarios.csv``
  13-week forecast table (week × scenario) with cash-in, cash-out, ending cash,
  and buffer trigger flags.

- ``ch19_cash_assumptions.csv``
  Scenario assumptions (what changed and why).

- ``ch19_cash_governance_template.csv``
  A starter governance table: owners, cadence, artifacts, escalation triggers.

Design + narrative (JSON/MD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``ch19_design.json``
  Machine-readable design choices: scenario definitions, buffer policy,
  pattern window.

- ``ch19_memo.md``
  A short planning memo including a base forecast summary.

Figures (PNG) + manifest
^^^^^^^^^^^^^^^^^^^^^^^^

Figures are written under:

``outputs/track_d/figures``

and listed in:

- ``ch19_figures_manifest.csv``

Interpretation guardrails
-------------------------

- A 13-week cash forecast is a **planning tool**, not a guarantee.
- Be conservative with stress scenarios.
- Do not claim that cash outcomes are “caused” by a single factor.
  Working capital timing is usually a mix of receipts, payments, and policies.
- Keep an **assumptions log** and treat changes as part of governance.

End-of-chapter exercises
------------------------

1. Construct a 13-week cash forecast and document your collections and payment assumptions.
2. Stress test: delayed collections + supplier terms change. Propose mitigations.
3. Define “cash governance”: who updates, cadence, and escalation rules.
