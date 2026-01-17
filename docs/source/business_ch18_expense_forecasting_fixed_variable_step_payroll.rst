Track D — Chapter 18
====================

Expense forecasting (fixed / variable / step costs, with payroll scenarios)
---------------------------------------------------------------------------

Revenue forecasts are only half of planning. For most small businesses, *expense behavior* is
what turns a “forecast” into an **action plan**.

This chapter introduces an accountant-friendly way to forecast expenses without pretending you
have a perfect cost model:

- **Fixed costs**: largely unchanged month to month (rent, many subscriptions).
- **Variable costs**: move with activity (utilities, processing fees, shipping).
- **Step costs**: stay flat until you cross a capacity threshold (staffing / payroll).

Payroll is the most important step cost in the NSO running case, so we build a simple payroll
forecast using **scenarios**.

What you will build
-------------------

1) An expense table by account (monthly)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will compute monthly totals for key operating expense accounts from the GL:

- Rent (6100)
- Utilities (6200)
- Payroll (6300)
- Depreciation (6400)
- Payroll tax (6500)
- Interest (6600)

COGS is excluded here on purpose: COGS is usually modeled alongside **revenue**.

2) A cost behavior map
^^^^^^^^^^^^^^^^^^^^^^

You will produce a mapping that classifies each expense line by:

- cost behavior (fixed / variable / step)
- controllable vs non-controllable
- suggested forecasting method
- suggested monitoring KPI

This is the bridge between “statistics” and “budget accountability.”

3) Payroll forecast with scenarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Payroll is forecast using a simple driver model:

- start with a **baseline** monthly gross wages estimate from history
- apply a **scenario multiplier** (Lean / Base / Growth)
- apply a small monthly wage inflation assumption
- estimate employer payroll tax using the historical rate (from the simulator)

This is not a causal model. It is a planning model.

Data source
-----------

This chapter uses:

- ``gl_journal.csv`` + ``chart_of_accounts.csv`` (expense totals by month)
- ``payroll_events.csv`` (payroll accruals and employer tax accruals)

How to run Chapter 18
---------------------

Prerequisite: generate the NSO dataset (once)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already ran Chapters 14–17, you already have NSO v1 in:

``data/synthetic/nso_v1``

If not:

.. code-block:: bash

   make business-nso-sim
   make business-validate

Run the Chapter 18 analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   make business-ch18

By default this runs:

.. code-block:: bash

   python -m scripts.business_ch18_expense_forecasting_fixed_variable_step_payroll \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs
-------

All artifacts are written under:

``outputs/track_d``

Core tables (CSV)
^^^^^^^^^^^^^^^^^

- ``ch18_expense_monthly_by_account.csv``
  History table: one row per month, one column per key expense account.

- ``ch18_expense_behavior_map.csv``
  The cost behavior + controllability map (this is a “budget rubric”).

- ``ch18_payroll_monthly.csv``
  Payroll accrual history by month (gross wages + employer tax).

- ``ch18_payroll_scenarios_forecast.csv``
  Payroll forecast for the next 12 months under Lean/Base/Growth scenarios.

- ``ch18_expense_forecast_next12_detail.csv``
  Long-form forecast table (month × scenario × account line).

- ``ch18_expense_forecast_next12_summary.csv``
  Wide summary (month × scenario) with totals and controllable subtotal.

- ``ch18_control_plan_template.csv``
  A starter “expense control plan” table (owners / KPIs / cadence).

Design + narrative (JSON/MD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``ch18_design.json``
  Machine-readable assumptions (scenario multipliers, inflation, employer tax rate).

- ``ch18_memo.md``
  A short planning memo with the next-12 summary table.

Figures (PNG) + manifest
^^^^^^^^^^^^^^^^^^^^^^^^

Figures are written under:

``outputs/track_d/figures``

and listed in:

- ``ch18_figures_manifest.csv``

Figures include:

- expense history by category
- payroll forecast overlay (Lean/Base/Growth)

Interpretation guardrails
-------------------------

- Treat the outputs as a **budget baseline**, not “the truth.”
- Do not claim that revenue *causes* expenses in this chapter. We only classify and project.
- Always pair the forecast with an **assumptions log** and owners for the controllable lines.

End-of-chapter exercises
------------------------

1. Add a new scenario (e.g., “Aggressive growth”) and explain the staffing plan behind it.
2. Replace the utilities forecast with a simple “% of revenue” assumption. Compare results.
3. Build a one-page expense control dashboard spec: thresholds + owners + escalation rules.
