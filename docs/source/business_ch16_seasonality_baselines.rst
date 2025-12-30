Track D — Chapter 16
=================

Seasonality and Seasonal Baselines (NSO running case)
-----------------------------------------------------

Chapter 15 showed how to produce a *defensible baseline forecast* using simple methods and a
12-month backtest.

Chapter 16 adds one major realism upgrade: **seasonality**.

In accounting-shaped business data, it’s common for revenue (and sometimes COGS) to follow
calendar patterns:

- holiday spikes,
- summer slowdowns,
- predictable quarter-end effects,
- predictable “busy months” and “quiet months.”

If a series has seasonality, a non-seasonal baseline (like ``naive_last``) can produce a forecast
that is systematically wrong in the same direction every year.

What you will build
-------------------

1) A month-of-year seasonality profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will compute a simple seasonal profile from history:

- month-of-year mean revenue (1..12)
- seasonal index = (month mean) / (overall mean)

This is not “fancy” time series decomposition. It is intentionally explainable and audit-friendly.

2) Seasonal baselines + backtest metrics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will compare five baseline methods on a 12-month holdout window:

Non-seasonal baselines (from Chapter 15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``naive_last`` — next month equals the last observed month
- ``moving_avg_3`` — next month equals the average of the last 3 months
- ``linear_trend`` — fit a straight line and extrapolate

Seasonal baselines (new)
~~~~~~~~~~~~~~~~~~~~~~~~

- ``seasonal_naive_12`` — reuse last year’s value for the same calendar month
- ``seasonal_mean`` — forecast each month as the mean of that calendar month in history

Selection rule (same as Chapter 15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pick the method with **lowest MAPE** on the 12-month holdout (tie-break on MAE).

Data source
-----------

This chapter uses the NSO income statement monthly table:

- ``data/synthetic/nso_v1/statements_is_monthly.csv``

The script pivots the income statement into a clean monthly wide table and forecasts **revenue**
(the Sales Revenue line).

How to run Chapter 16
---------------------

Prerequisite: generate the NSO dataset (once)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already ran Chapter 14/15, you already have NSO v1 in:

``data/synthetic/nso_v1``

If not:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Run the Chapter 16 analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-ch16

By default this runs:

.. code-block:: bash

   python -m scripts.business_ch16_seasonality_baselines \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
-------

All artifacts are written under:

``outputs/track_d/track_d``

Core tables (CSV)
^^^^^^^^^^^^^^^^^

- ``ch16_series_monthly.csv``  
  Clean monthly series used in this chapter (revenue + key income statement lines + month keys).

- ``ch16_seasonal_profile.csv``  
  Month-of-year mean revenue and seasonal index (mean / overall mean).

- ``ch16_backtest_predictions.csv``  
  Month-by-month predictions for each method on the holdout year.

- ``ch16_backtest_metrics.csv``  
  MAE/MAPE by method (this is the best file to open first).

- ``ch16_forecast_next12.csv``  
  Selected method forecast for the next 12 months, including a simple range.

Design + narrative (JSON/MD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``ch16_design.json``  
  Machine-readable cover sheet: methods, windows, selection rule, chosen method.

- ``ch16_memo.md``  
  Short memo: seasonal profile highlights + backtest results + next-12 forecast table.

Figures (PNG) + manifest
^^^^^^^^^^^^^^^^^^^^^^^^

Figures are written under:

``outputs/track_d/track_d/figures``

and listed in:

- ``ch16_figures_manifest.csv``

Figures include:

- seasonal index by month-of-year
- backtest overlay for the selected method
- next-12 forecast overlay

Troubleshooting
---------------

“Chapter 16 requires 24 months…”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Chapter 16 runs a 12/12 backtest. You need at least 24 months of monthly data.

“Expected statements_is_monthly.csv … but not found.”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Confirm you ran the simulator and that ``--datadir`` points to the NSO folder:

- Correct: ``--datadir data/synthetic/nso_v1``

What’s next (Chapter 17+)
-------------------------

- Chapter 17: rolling forecasts + scenario planning
- Chapter 18: forecasting with drivers (combine operational drivers + time series)

End-of-chapter exercises
------------------------

1. Run Chapter 16 but forecast **COGS** (instead of revenue). Do seasonal methods help?
2. Change the selection rule to “min MAE” and compare which method wins.
3. Identify one month that looks like an outlier. Explain how it could bias seasonal means.
