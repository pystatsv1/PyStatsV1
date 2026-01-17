Track D — Chapter 20
====================

Integrated forecasting (P&L + balance sheet + cash tie-out)
-----------------------------------------------------------

In Chapter 19 you learned how to build a short-term cash forecast.
In practice, most organizations also maintain a **medium-term** plan (often 12 months)
that ties together:

- **Profit & loss** (accrual): what the business earns and spends.
- **Balance sheet** (stocks): what the business owns/owes at month-end.
- **Cash flow** (flows): how we get from beginning cash to ending cash.

The key idea is simple:

**A forecast is not finished until the three statements reconcile.**

If profit goes up but cash goes down, the model should explain it through
working capital (AR/inventory/AP), capex, or financing.

Learning objectives
-------------------

By the end of this chapter you will be able to:

- Build a 12‑month integrated forecast that ties P&L, balance sheet, and cash.
- Forecast key balance sheet drivers (AR, inventory, AP, debt, fixed assets).
- Reconcile cash using a bridge and surface any **residual** explicitly.
- Explain “profit up, cash down” using working-capital logic.

Data source (NSO v1)
--------------------

This chapter uses the simulator’s statement tables:

- ``statements_is_monthly.csv`` (income statement)
- ``statements_bs_monthly.csv`` (balance sheet)
- ``statements_cf_monthly.csv`` (cash flow bridge lines)

We treat these as the **canonical truth** for the historical period, and then
use simple, accountant-friendly rules to extend the model forward.

Walkthrough: how the tie-out works
----------------------------------

1) Forecast the P&L
^^^^^^^^^^^^^^^^^^^

We build a baseline revenue forecast using a **seasonal naive** approach
(each future month starts from the average of that calendar month in history).

Then we forecast costs using simple **rates**:

- COGS is forecast as a recent median COGS-to-revenue ratio.
- Operating expenses are forecast as a recent median opex-to-revenue ratio.

This keeps the focus on the integration logic (not fancy forecasting methods).

2) Forecast key balance sheet items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We forecast working capital using “days” heuristics:

- **DSO** (days sales outstanding) → AR ≈ revenue × DSO / 30
- **DIO** (days inventory outstanding) → inventory ≈ COGS × DIO / 30
- **DPO** (days payable outstanding) → AP ≈ COGS × DPO / 30

We also carry forward debt and fixed assets using simple rules:

- Capex is estimated from recent cash capex and increases PP&E cost.
- Depreciation increases accumulated depreciation (a contra asset).
- Notes payable decreases by a typical principal payment (if present).

3) Reconcile cash
^^^^^^^^^^^^^^^^^

Cash is reconciled using a bridge:

.. math::

   \Delta Cash \approx Net\ Income + Depreciation - \Delta AR - \Delta Inventory + \Delta AP
   \; + \; Investing \; + \; Financing

We write the bridge explicitly and compute a **residual** (difference between
the bridge and the balance sheet cash). Ideally it is near zero; if not, it is
a signal the assumptions need review.

How to run Chapter 20
---------------------

Prerequisite: generate the NSO dataset (once)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already ran Chapters 14–19, you already have NSO v1 in:

``data/synthetic/nso_v1``

If not:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Run the Chapter 20 analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-ch20

By default this runs:

.. code-block:: bash

   python -m scripts.business_ch20_integrated_forecasting_three_statements \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
-------

All artifacts are written under:

``outputs/track_d``

Core tables (CSV)
^^^^^^^^^^^^^^^^^

- ``ch20_pnl_forecast_monthly.csv``
- ``ch20_balance_sheet_forecast_monthly.csv``
- ``ch20_cash_flow_forecast_monthly.csv``
- ``ch20_assumptions.csv``

Meta artifacts
^^^^^^^^^^^^^^

- ``ch20_design.json``
- ``ch20_memo.md``
- ``ch20_figures_manifest.csv`` + figures in ``outputs/track_d/figures/``

End-of-chapter problems
-----------------------

1) Build an integrated skeleton and reconcile the three statements.

2) Working capital scenario: show profit up but cash down and explain.

3) Identify three common integration errors and how to catch them.
