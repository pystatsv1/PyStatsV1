Track D chapter index (PyPI)
============================

This page is a "table of contents" for running Track D from the PyPI workbook.

After you've initialized a Track D workbook:

.. code-block:: bash

   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

You can run any chapter with:

.. code-block:: bash

   pystatsv1 workbook run d01

By default, scripts write to ``outputs/track_d/``. See :doc:`track_d_outputs_guide`.

.. contents:: On this page
   :local:
   :depth: 2

.. _track_d_run_d00peekdata:

D00PEEKDATA — peek at the (canonical) datasets.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d00_peek_data

Expected artifacts (written under ``outputs/track_d/``):

- ``d00_peek_data_summary.md``

.. _track_d_run_d00setupdata:

D00SETUPDATA — (re)generate the synthetic datasets.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d00_setup_data

Expected artifacts (written under ``outputs/track_d/``):

- ``data/synthetic/ledgerlab_ch01/  (LedgerLab seed=123 tables)``
- ``data/synthetic/nso_v1/          (NSO v1 seed=123 tables)``
- ``outputs/track_d/d00_setup_data_validate/  (optional validation artifacts)``

.. _track_d_run_d01:

D01 — Accounting as a measurement system.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d01

Expected artifacts (written under ``outputs/track_d/``):

- ``business_ch01_cash_balance.png``
- ``business_ch01_balance_sheet_bar.png``
- ``business_ch01_summary.json``

Read the chapter narrative (main docs): `D01 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch01_accounting_measurement.html>`_

.. _track_d_run_d02:

D02 — Double-entry and the general ledger as a database.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d02

Expected artifacts (written under ``outputs/track_d/``):

- ``business_ch02_gl_tidy.csv``
- ``business_ch02_trial_balance.csv``
- ``business_ch02_account_rollup.csv``
- ``business_ch02_tb_by_account.png``
- ``business_ch02_summary.json``

Read the chapter narrative (main docs): `D02 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch02_double_entry_and_gl.html>`_

.. _track_d_run_d03:

D03 — Financial statements as summary statistics.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d03

Expected artifacts (written under ``outputs/track_d/``):

- ``business_ch03_summary.json``
- ``business_ch03_statement_bridge.csv``
- ``business_ch03_trial_balance.csv``
- ``business_ch03_net_income_vs_cash_change.png``

Read the chapter narrative (main docs): `D03 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch03_statements_as_summaries.html>`_

.. _track_d_run_d04:

D04 — Assets: inventory, fixed assets, depreciation (and leases, conceptual).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d04

Expected artifacts (written under ``outputs/track_d/``):

- ``business_ch04_inventory_rollforward.csv``
- ``business_ch04_margin_bridge.csv``
- ``business_ch04_depreciation_rollforward.csv``
- ``business_ch04_summary.json``
- ``business_ch04_gross_margin_over_time.png``
- ``business_ch04_depreciation_over_time.png``

Read the chapter narrative (main docs): `D04 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch04_assets_inventory_fixed_assets.html>`_

.. _track_d_run_d05:

D05 — Liabilities, payroll, taxes, and equity: obligations and structure.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d05

Expected artifacts (written under ``outputs/track_d/``):

- ``business_ch05_summary.json``
- ``business_ch05_wages_payable_rollforward.csv``
- ``business_ch05_payroll_taxes_payable_rollforward.csv``
- ``business_ch05_sales_tax_payable_rollforward.csv``
- ``business_ch05_notes_payable_rollforward.csv``
- ``business_ch05_accounts_payable_rollforward.csv``
- ``business_ch05_liabilities_over_time.png``

Read the chapter narrative (main docs): `D05 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch05_liabilities_payroll_taxes_equity.html>`_

.. _track_d_run_d06:

D06 — Reconciliations as quality control.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d06

Expected artifacts (written under ``outputs/track_d/``):

- ``ar_rollforward.csv``
- ``bank_recon_matches.csv``
- ``bank_recon_exceptions.csv``
- ``ch06_summary.json``

Read the chapter narrative (main docs): `D06 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch06_reconciliations_quality_control.html>`_

.. _track_d_run_d07:

D07 — Preparing accounting data for analysis.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d07

Expected artifacts (written under ``outputs/track_d/``):

- ``gl_tidy.csv``
- ``gl_monthly_summary.csv``
- ``ch07_summary.json``

Read the chapter narrative (main docs): `D07 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch07_preparing_accounting_data_for_analysis.html>`_

.. _track_d_run_d08:

D08 — Descriptive statistics for financial performance.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d08

Expected artifacts (written under ``outputs/track_d/``):

- ``gl_kpi_monthly.csv``
- ``ar_monthly_metrics.csv``
- ``ar_payment_slices.csv``
- ``ar_days_stats.csv``
- ``ch08_summary.json``

Read the chapter narrative (main docs): `D08 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch08_descriptive_statistics_financial_performance.html>`_

.. _track_d_run_d09:

D09 — Plotting/reporting style contract + example outputs.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d09

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch09_style_contract.json``
- ``ch09_figures_manifest.csv``
- ``ch09_executive_memo.md``
- ``ch09_summary.json``

Read the chapter narrative (main docs): `D09 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch09_reporting_style_contract.html>`_

.. _track_d_run_d10:

D10 — Probability and Risk in Business Terms.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d10

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch10_figures_manifest.csv``
- ``ch10_risk_memo.md``
- ``ch10_risk_summary.json``

Read the chapter narrative (main docs): `D10 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch10_probability_risk.html>`_

.. _track_d_run_d11:

D11 — Sampling and Estimation (Audit and Controls Lens).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d11

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch11_sampling_plan.json``
- ``ch11_sampling_summary.json``
- ``ch11_audit_memo.md``
- ``ch11_figures_manifest.csv``

Read the chapter narrative (main docs): `D11 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch11_sampling_estimation_audit_controls.html>`_

.. _track_d_run_d12:

D12 — Hypothesis Testing for Decisions (Practical, Not Math-Heavy).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d12

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch12_experiment_design.json``
- ``ch12_hypothesis_testing_summary.json``
- ``ch12_experiment_memo.md``
- ``ch12_figures_manifest.csv``

Read the chapter narrative (main docs): `D12 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch12_hypothesis_testing_decisions.html>`_

.. _track_d_run_d13:

D13 — Correlation, Causation, and Controlled Comparisons (NSO running case).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d13

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch13_controlled_comparisons_design.json``
- ``ch13_correlation_summary.json``
- ``ch13_correlation_memo.md``
- ``ch13_figures_manifest.csv``

Read the chapter narrative (main docs): `D13 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch13_correlation_causation_controlled_comparisons.html>`_

.. _track_d_run_d14:

D14 — Regression Driver Analysis (NSO).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d14

Read the chapter narrative (main docs): `D14 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch14_regression_driver_analysis.html>`_

.. _track_d_run_d15:

D15 — Forecasting foundations (NSO).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d15

Read the chapter narrative (main docs): `D15 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch15_forecasting_foundations.html>`_

.. _track_d_run_d16:

D16 — Seasonality and baseline forecasts (NSO).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d16

Read the chapter narrative (main docs): `D16 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch16_seasonality_baselines.html>`_

.. _track_d_run_d17:

D17 — Revenue forecasting via segmentation + drivers (NSO v1).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d17

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch17_ar_revenue_segment_monthly.csv``
- ``ch17_series_monthly.csv``
- ``ch17_customer_segments.csv``
- ``ch17_backtest_metrics.csv``
- ``ch17_backtest_total_revenue.csv``
- ``ch17_forecast_next12.csv``
- ``ch17_memo.md``
- ``ch17_design.json``
- ``ch17_known_events_template.json``
- ``ch17_figures_manifest.csv``
- ``ch17_manifest.json``
- ``ch17_forecast_next_12m.csv``
- ``ch17_forecast_memo.md``

Read the chapter narrative (main docs): `D17 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch17_revenue_forecasting_segmentation_drivers.html>`_

.. _track_d_run_d18:

D18 — Expense forecasting (NSO running case).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d18

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch18_expense_monthly_by_account.csv``
- ``ch18_expense_behavior_map.csv``
- ``ch18_payroll_monthly.csv``
- ``ch18_payroll_scenarios_forecast.csv``
- ``ch18_expense_forecast_next12_detail.csv``
- ``ch18_expense_forecast_next12_summary.csv``
- ``ch18_control_plan_template.csv``
- ``ch18_design.json``
- ``ch18_memo.md``
- ``ch18_figures_manifest.csv``

Read the chapter narrative (main docs): `D18 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch18_expense_forecasting_fixed_variable_step_payroll.html>`_

.. _track_d_run_d19:

D19 — Cash flow forecasting (direct method, 13-week).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d19

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch19_cash_history_weekly.csv``
- ``ch19_cash_forecast_13w_scenarios.csv``
- ``ch19_cash_assumptions.csv``
- ``ch19_cash_governance_template.csv``
- ``ch19_design.json``
- ``ch19_memo.md``
- ``ch19_figures_manifest.csv``

Read the chapter narrative (main docs): `D19 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch19_cash_flow_forecasting_direct_method_13_week.html>`_

.. _track_d_run_d20:

D20 — Integrated forecasting (P&L + balance sheet + cash tie-out).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d20

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch20_pnl_forecast_monthly.csv``
- ``ch20_balance_sheet_forecast_monthly.csv``
- ``ch20_cash_flow_forecast_monthly.csv``
- ``ch20_assumptions.csv``
- ``ch20_design.json``
- ``ch20_memo.md``
- ``ch20_figures_manifest.csv``

Read the chapter narrative (main docs): `D20 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch20_integrated_forecasting_three_statements.html>`_

.. _track_d_run_d21:

D21 — scenario planning, sensitivity, and stress testing.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d21

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch21_scenario_pack_monthly.csv``
- ``ch21_sensitivity_cash_shortfall.csv``
- ``ch21_assumptions.csv``
- ``ch21_governance_template.csv``
- ``ch21_figures_manifest.csv``
- ``ch21_design.json``
- ``ch21_memo.md``

Read the chapter narrative (main docs): `D21 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch21_scenario_planning_sensitivity_stress.html>`_

.. _track_d_run_d22:

D22 — Financial statement analysis toolkit.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d22

Expected artifacts (written under ``outputs/track_d/``):

- ``figures/``
- ``ch22_ratios_monthly.csv``
- ``ch22_common_size_is.csv``
- ``ch22_common_size_bs.csv``
- ``ch22_variance_bridge_latest.csv``
- ``ch22_assumptions.csv``
- ``ch22_figures_manifest.csv``
- ``ch22_memo.md``
- ``ch22_design.json``

Read the chapter narrative (main docs): `D22 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch22_financial_statement_analysis_toolkit.html>`_

.. _track_d_run_d23:

D23 — Communicating results (memos, dashboards, governance).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run:

.. code-block:: bash

   pystatsv1 workbook run d23

Expected artifacts (written under ``outputs/track_d/``):

- ``ch23_memo_template.md``
- ``ch23_kpi_governance_template.csv``
- ``ch23_dashboard_spec_template.csv``
- ``ch23_red_team_checklist.md``
- ``ch23_design.json``

Read the chapter narrative (main docs): `D23 narrative <https://pystatsv1.readthedocs.io/en/latest/business_ch23_communicating_results_governance.html>`_
