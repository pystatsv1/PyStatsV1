PyStatsV1 documentation
=======================

Welcome to the documentation for **PyStatsV1** – chapter-based applied statistics examples in plain Python, mirroring classical R textbook analyses.

Students (recommended): install from PyPI and start the Workbook
----------------------------------------------------------------

If you're a student (not a developer), the easiest path is to install the Workbook bundle
from PyPI and let the CLI create a local copy of the labs for you.

.. code-block:: bash

   python -m pip install "pystatsv1[workbook]"
   pystatsv1 workbook init ./my_workbook

Then run the built-in checks as you work:

.. code-block:: bash

   cd my_workbook
   pystatsv1 workbook check

If you're on Windows 11 and this is your first time installing Python, start here:
:doc:`workbook/windows11_setup`.

Lightweight install (no Workbook checks)
----------------------------------------

If you only want the core helper package (without the Workbook checks bundle), you can
install the base package directly from PyPI:

.. code-block:: bash

   python -m pip install pystatsv1

Developers / Contributing
-------------------------

If you want the full chapter-based labs (simulators, scripts, Makefile targets, and tests),
clone the GitHub repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1
   python -m pip install -e .

See :doc:`getting_started` and :doc:`contributing` for the contributor workflow.

.. toctree::
   :maxdepth: 1
   :caption: Workbook – Student Labs (recommended starting point)

   workbook/index

.. toctree::
   :maxdepth: 2
   :caption: Track A – Applied Statistics with Python (Regression)

   getting_started
   applied_stats_with_python_intro
   applied_stats_with_python_ch2_r_basics
   applied_stats_with_python_ch3_data_and_programming
   applied_stats_with_python_ch4_summarizing_data
   applied_stats_with_python_ch5_probability_and_statistics
   applied_stats_with_python_ch6_resources
   applied_stats_with_python_ch7_simple_linear_regression
   applied_stats_with_python_ch8_inference_for_simple_linear_regression
   applied_stats_with_python_ch9_multiple_linear_regression
   applied_stats_with_python_ch10_model_building
   applied_stats_with_python_ch11_categorical_predictors_and_interactions
   applied_stats_with_python_ch12_analysis_of_variance.rst
   applied_stats_with_python_ch13_model_diagnostics
   applied_stats_with_python_ch14_transformations
   applied_stats_with_python_ch15_collinearity
   applied_stats_with_python_ch16_variable_selection_and_model_building
   applied_stats_with_python_ch17_logistic_regression
   applied_stats_with_python_ch18_beyond
   
   chapters
   teaching_guide
   contributing

.. _psych-track:

.. toctree::
   :maxdepth: 1
   :caption: Track B – Psychological Science & Statistics (Psych track)

   psych_intro
   psych_ch1_thinking_like_a_scientist
   psych_ch2_ethics
   psych_ch3_measuring_variables
   psych_ch4_distributions
   psych_ch5_central_variability
   psych_ch6_normal_zscores
   psych_ch7_probability_sampling
   psych_ch8_hypothesis_testing
   psych_ch9_one_sample_ci
   psych_ch10_independent_t
   psych_ch11_paired_t
   psych_ch12_one_way_anova
   psych_ch13_two_way_anova
   psych_ch14_repeated_measures_anova
   psych_ch14a_pingouin_appendix
   psych_ch15_correlation
   psych_ch15a_pingouin_appendix
   psych_ch16_regression
   psych_ch16a_pingouin_regression
   psych_ch16b_pingouin_regression
   psych_ch17_mixed_models
   psych_ch18_ancova
   psych_ch19_nonparametrics
   psych_ch19a_rank_nonparametrics
   psych_ch20_responsible_researcher



.. _psych-track-c:

.. toctree::
   :maxdepth: 1
   :caption: Track C – Problem Sets & Worked Solutions (Psych track)

   psych_track_c_overview
   psych_ch10_problem_set
   psych_ch11_problem_set
   psych_ch12_problem_set
   psych_ch13_factorial_anova
   psych_ch14_problem_set
   psych_ch15_problem_set
   psych_ch16_problem_set
   psych_ch17_problem_set
   psych_ch18_problem_set
   psych_ch19_problem_set
   psych_ch20_problem_set


.. _business-track-d:

.. toctree::
   :maxdepth: 1
   :caption: Track D – Business Statistics & Forecasting for Accountants

   business_intro
   business_ch01_accounting_measurement
   business_ch02_double_entry_and_gl
   business_ch03_statements_as_summaries
   business_ch04_assets_inventory_fixed_assets
   business_ch05_liabilities_payroll_taxes_equity
   business_ch06_reconciliations_quality_control
   business_ch07_preparing_accounting_data_for_analysis
   business_ch08_descriptive_statistics_financial_performance
   business_appendix_ch08_milestone_big_picture
   business_ch09_reporting_style_contract
   business_ch10_probability_risk
   business_ch11_sampling_estimation_audit_controls
   business_ch12_hypothesis_testing_decisions
   business_ch13_correlation_causation_controlled_comparisons
   business_ch14_regression_driver_analysis
   business_appendix_ch14_milestone_track_d_data
   business_appendix_ch14b_nso_v1_data_dictionary
   business_appendix_ch14c_ch14_artifact_dictionary
   business_appendix_ch14d_artifact_qa_checklist_big_picture
   business_appendix_ch14e_apply_to_real_world
   business_ch15_forecasting_foundations
   business_ch16_seasonality_baselines
   business_ch17_revenue_forecasting_segmentation_drivers
   business_appendix_pdf_refresher
   business_appendix_authoring_rules