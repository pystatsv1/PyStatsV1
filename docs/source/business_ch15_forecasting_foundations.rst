Track D — Chapter 15
====================

Forecasting Foundations and Forecast Hygiene (NSO running case)
--------------------------------------------------------------

In Chapter 14 you built an **explainable driver model** (COGS explained by operational activity).
In Chapter 15 you switch gears: you treat the accounting output as a **time series** and learn how
to produce a **defensible baseline forecast**.

This chapter is deliberately “low-tech” on purpose:

- You will compare **three simple baseline forecasts**.
- You will **backtest** them on a 12-month holdout window.
- You will pick a method using **error metrics**, not vibes.
- You will create an **assumptions log template** so your forecast is auditable.

The goal is not to build the best forecast possible. The goal is to build a forecast process
that an accountant/analyst can explain, reproduce, and improve.

What is “forecast hygiene”?
---------------------------

Forecast hygiene is the set of practices that keeps forecasting useful and honest:

- **Define the question** (what are we forecasting, for whom, and for what decision?).
- **Define the grain** (monthly vs weekly vs daily; consolidated vs by product/location).
- **Document assumptions** (what is expected to change and why).
- **Measure error** with backtesting (how wrong have we been, using history?).
- **Version the artifacts** (inputs, method choice, metrics, memo, and figures).

In accounting, this matters because forecasts often feed budgeting, cash planning, staffing,
and performance conversations. A forecast that can’t be explained or reproduced becomes
a source of risk.

How this ties to earlier chapters
---------------------------------

Chapter 15 builds directly on concepts you have already practiced:

- **Chapter 7–9 (data prep + reporting discipline):** consistent month keys, clean joins, and
  reliable output artifacts.
- **Chapter 13 (controlled comparisons):** “compare like with like” is the mindset behind
  backtesting (train vs holdout).
- **Chapter 14 (driver lens):** the forecast is still a *driver lens* (planning tool), not a claim
  of causation or a guarantee.

What you will build
-------------------

A clean monthly time series (from the NSO income statement)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From ``statements_is_monthly.csv`` you will build a wide monthly table:

- ``month`` (YYYY-MM)
- ``revenue`` (Sales Revenue)
- ``cogs`` (Cost of Goods Sold)
- ``gross_profit``
- ``operating_expenses``
- ``net_income``

Three baseline forecasts (for revenue)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will compare three baseline methods:

1. **naive_last** — next month equals the last observed month
2. **moving_avg_3** — next month equals the average of the last 3 months
3. **linear_trend** — fit a straight line through time and extrapolate

A 12-month backtest + error metrics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will hold out the last 12 months, forecast them using the first 12 months, and compute:

- **MAE** (mean absolute error): typical size of the miss (in currency units)
- **MAPE** (mean absolute percentage error): typical miss as a percent of actual

Then you will select the baseline method with the lowest MAPE (tie-break on MAE).

A forecast memo + auditable assumptions log
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will produce a short memo and an ``assumptions log`` CSV template so that:

- the forecast is shareable with stakeholders,
- the method selection is documented,
- the “why” behind adjustments is captured in a durable, versioned form.

How to run Chapter 15
---------------------

Prerequisite: generate the NSO dataset (once)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already ran Chapter 14, you likely already have the NSO dataset at:

``data/synthetic/nso_v1``

If not:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Run the Chapter 15 analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-ch15

By default this runs:

.. code-block:: bash

   python -m scripts.business_ch15_forecasting_foundations \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
-------

All artifacts are written under:

``outputs/track_d/track_d``

**Open this first (recommended order):**

1. ``ch15_backtest_metrics.csv`` (which baseline wins?)
2. ``figures/ch15_fig_backtest_overlay.png`` (does the chosen method track reality?)
3. ``ch15_forecast_memo.md`` (shareable summary)
4. ``ch15_forecast_next12.csv`` (numbers you plug into planning)


Core tables (CSV)
^^^^^^^^^^^^^^^^^

- ``ch15_series_monthly.csv``  
  Clean monthly time series used for forecasting (revenue + key IS lines).

- ``ch15_backtest_predictions.csv``  
  Month-by-month backtest predictions for each method (actual vs predicted + errors).

- ``ch15_backtest_metrics.csv``  
  Summary metrics (MAE and MAPE) by method.

- ``ch15_forecast_next12.csv``  
  Selected baseline method forecast for the next 12 months, including a simple range.

- ``ch15_assumptions_log_template.csv``  
  Template you fill in when business context requires adjustments.

Design + narrative (JSON/MD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``ch15_forecast_design.json``  
  Machine-readable “cover sheet”: series, train/test windows, methods compared,
  selection rule, chosen method, and forecast months.

- ``ch15_forecast_memo.md``  
  Human-readable memo with a small metrics table and the forecast table.

Figures (PNG) + manifest
^^^^^^^^^^^^^^^^^^^^^^^^

Figures are written under ``outputs/track_d/track_d/figures`` and listed in:

- ``ch15_figures_manifest.csv``

Troubleshooting
---------------

“Expected statements_is_monthly.csv … but not found.”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You likely pointed ``--datadir`` at the wrong folder.

- Correct: ``--datadir data/synthetic/nso_v1``
- Also confirm you ran: ``make business-nso-sim``

Outputs are missing or in a surprising folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chapter writes into ``--outdir`` plus ``/track_d`` (to match Track D conventions).

What’s next (Chapter 16+)
-------------------------

- Chapter 16: seasonality and seasonal baselines
- Chapter 17: rolling forecasts + scenario planning
- Chapter 18: forecasting with drivers (combine operational drivers + time series)

End-of-chapter exercises
------------------------

1. Re-run Chapter 15 but forecast **COGS** instead of revenue.
2. Change the holdout window to 6 months. Does the best baseline method change?
3. Use the assumptions log template to document a hypothetical pricing change next quarter.

See also
--------
- Appendix 14D (Artifact QA checklist): use the same pre-share mindset before circulating forecasts.
- Appendix 14E (Apply to real world): adapting the workflow to your own chart of accounts and datasets.