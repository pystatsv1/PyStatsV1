.. _psych_ch16b_pingouin_regression:

======================================================
Chapter 16b – Regression Diagnostics with Pingouin
======================================================

*Track B: Psychological Science & Statistics – Appendix to Chapter 16*

Overview
========

In Chapter 16, we introduced linear regression as a tool for prediction
and interpretation. We focused on

* the **line of best fit** (:math:`Y' = bX + a`),
* the **least squares** criterion,
* the **standard error of the estimate**, and
* **multiple regression** (predicting behavior from multiple variables).

However, a good PyStatsV1 workflow does **not** stop after fitting a model.
We must *engineer* our results by checking whether the model and the data
behave as the assumptions require.

This appendix shows how to:

* use :mod:`pingouin` to fit a multiple regression model,
* compute standard regression diagnostics (residuals, leverage,
  Cook's distance),
* identify potentially influential observations, and
* illustrate the dangers of relying only on summary statistics using
  **Anscombe's Quartet**.

The goal is to give students a reproducible, testable set of tools they can
reuse in their own projects.

Learning goals
==============

After working through this appendix, you should be able to:

1. Explain the difference between **good fit** (e.g., high :math:`R^2`)
   and **good model** (reasonable assumptions).
2. Interpret standard regression diagnostics:

   * residuals and standardized residuals,
   * leverage (hat values),
   * Cook's distance.

3. Use :mod:`pingouin`'s regression tools together with NumPy and
   pandas to compute these diagnostics.
4. Explain how **Anscombe's Quartet** shows that

   * identical means, variances, and correlations can hide very different
     data patterns,
   * visualization and diagnostics are crucial in a PyStatsV1 workflow.

Files for this appendix
=======================

This appendix uses the following PyStatsV1 files:

* **Script**: ``scripts/psych_ch16b_pingouin_regression_diagnostics.py``

  - simulates a psychology regression dataset (reusing the Chapter 16
    data generator),
  - fits a multiple regression model with :func:`pingouin.linear_regression`,
  - computes regression diagnostics (residuals, leverage, Cook's distance),
  - identifies the most influential observations,
  - generates diagnostic plots,
  - constructs and analyzes **Anscombe's Quartet** to demonstrate why
    diagnostics and visualization matter.

* **Tests**:
  ``tests/test_psych_ch16b_pingouin_regression_diagnostics.py``

  - verify that diagnostics have the expected shape and properties,
  - check that leverage behaves as theory predicts,
  - ensure that model :math:`R^2` is in a reasonable range,
  - run the full end-to-end pipeline in a temporary directory,
  - verify that CSV and PNG outputs are written correctly,
  - check that the Anscombe datasets have nearly identical summary
    statistics while having different shapes.

* **Makefile targets** (added in a separate CI branch):

  - ``make psych-ch16b`` – run the diagnostics demo (including
    Anscombe's Quartet),
  - ``make test-psych-ch16b`` – run tests for this appendix only.

.. note::

   As with previous chapters, the script is written in a way that makes
   it easy to import its functions into other projects or Jupyter
   notebooks. The tests treat regression diagnostics as *software*
   objects that can be checked, versioned, and reused.

Section 1 – Regression diagnostics in practice
==============================================

Recall that a linear regression model makes several assumptions:

* **Linearity** – the relationship between predictors and outcome is
  approximately linear.
* **Homoscedasticity** – the spread (variance) of residuals is roughly
  constant across the range of fitted values.
* **Independence** – residuals are not systematically related to each
  other (e.g., no strong time trends).
* **Normality of residuals** – residuals are approximately normally
  distributed.

The :mod:`pingouin` function :func:`pingouin.linear_regression` focuses
primarily on **estimation** and **inference**:

* regression coefficients and standard errors,
* :math:`t`-tests and :math:`p`-values,
* :math:`R^2` and adjusted :math:`R^2`.

To check assumptions, we need additional diagnostics. In
``psych_ch16b_pingouin_regression_diagnostics.py`` we therefore:

1. Simulate a dataset that extends the Chapter 16 example, with
   variables such as:

   * ``stress``
   * ``sleep_hours``
   * ``study_hours``
   * ``motivation``
   * ``exam_score`` (outcome)

2. Fit a multiple regression model predicting ``exam_score`` from
   several predictors.
3. Compute diagnostics using NumPy and pandas:

   * **fitted values** – model predictions :math:`\\hat{y}`,
   * **residuals** – observed minus fitted (:math:`y - \\hat{y}`),
   * **standardized residuals** – residuals scaled by their estimated
     standard deviation,
   * **leverage** – hat values on the diagonal of the hat matrix,
     :math:`H = X (X'X)^{-1} X'`,
   * **Cook's distance** – a measure of how much the regression
     coefficients would change if we removed a given observation.

4. Save the diagnostics to CSV and plot simple diagnostics:

   * **Residuals vs Fitted** plot – to check linearity and
     homoscedasticity.
   * **Leverage vs Cook's distance** plot – to identify high-leverage,
     influential observations.

Interpreting diagnostics (high level)
-------------------------------------

* Residuals should be roughly centered around zero. A clear curve or
  pattern in residuals vs fitted values suggests non-linearity.
* Leverage values near 0 indicate little influence on the model fit;
  values closer to 1 indicate observations that are far from the center
  of the predictor space.
* Cook's distance combines residual size and leverage. Points with
  unusually large Cook's distance are candidates for closer inspection.
  They are not automatically "bad" data points, but they may be
  influential.

Section 2 – Anscombe's Quartet
==============================

To see why diagnostics and visualization are essential, this appendix
includes a second dataset: **Anscombe's Quartet**.

Anscombe (1973) constructed four small datasets (I–IV) with the
following surprising property:

* Each dataset has nearly identical:

  - mean of :math:`x`,
  - mean of :math:`y`,
  - variance of :math:`x`,
  - variance of :math:`y`,
  - correlation :math:`r` between :math:`x` and :math:`y`,
  - regression line :math:`Y' = bX + a`.

* But when you plot them, the **shapes are completely different**:

  - One looks like a typical linear relationship.
  - One is clearly non-linear.
  - One is linear except for a single outlier.
  - One has a nearly perfect vertical line with one extreme point.

In other words, **summary statistics alone can mislead us**. Two
datasets can share the same correlation and regression line but tell
completely different stories once we visualize them.

How we use Anscombe's Quartet in PyStatsV1
------------------------------------------

The script ``psych_ch16b_pingouin_regression_diagnostics.py`` includes:

* a helper that constructs a tidy version of **Anscombe's Quartet**
  with columns

  - ``x``
  - ``y``
  - ``dataset`` (I, II, III, IV)

* a function that computes, for each dataset:

  - :math:`\\bar{x}`, :math:`\\bar{y}`,
  - :math:`s_x^2`, :math:`s_y^2`,
  - correlation :math:`r`,
  - simple regression line (:math:`a` and :math:`b`).

* a **2x2 grid of scatterplots** with

  - the same axis limits,
  - the fitted regression line overlaid,
  - one panel per dataset (I–IV).

The corresponding tests check that:

* all four datasets have nearly identical summary statistics, and
* the code produces the expected summary table and plot file.

Worked example (conceptual)
---------------------------

1. Run the diagnostics script (once your Makefile targets are wired):

   .. code-block:: bash

      make psych-ch16b

2. The script first runs the psychology regression diagnostics example
   (as described in Section 1).

3. Then the script constructs Anscombe's Quartet, computes summary
   statistics by dataset, and prints something like:

   .. code-block:: text

      Anscombe summary (per dataset):
        dataset   mean_x   mean_y   var_x   var_y     r       slope   intercept
      0       I    9.00    7.50   11.00    4.13  0.82      0.50      3.00
      1      II    9.00    7.50   11.00    4.13  0.82      0.50      3.00
      2     III    9.00    7.50   11.00    4.13  0.82      0.50      3.00
      3      IV    9.00    7.50   11.00    4.13  0.82      0.50      3.00

   The exact numbers may differ slightly due to floating point rounding,
   but the key idea is that the four datasets have almost identical
   summary statistics.

4. Finally, the script creates a 2x2 scatterplot figure and writes it to:

   * ``outputs/track_b/ch16b_anscombe_quartet.png``

   When you inspect this image, you will see four very different
   patterns, despite having "the same" regression summary.

Takeaway for students and instructors
-------------------------------------

Anscombe's Quartet makes two core points that align with the PyStatsV1
philosophy:

1. **Do not stop at statistics.**

   * A single number like :math:`r` or :math:`R^2` can hide very
     different data stories.
   * Always pair numerical output with plots and diagnostics.

2. **Treat models as software artifacts.**

   * In PyStatsV1, every substantial analysis step is backed by
     functions, tests, and CI checks.
   * Adding a new diagnostic (e.g., Cook's distance, Anscombe analysis)
     means adding new code *and* new tests.

Section 3 – The code: overview of key functions
===============================================

You do not need to memorize the exact implementation details, but it is
useful to know what the main functions do.

In ``scripts/psych_ch16b_pingouin_regression_diagnostics.py``:

* ``compute_regression_diagnostics(df, predictors, outcome)``

  - Fits a multiple regression model,

    .. math::
       exam\\_score \\sim study\\_hours + sleep\\_hours + stress + motivation,

  - returns a diagnostics DataFrame with

    * ``fitted``,
    * ``residual``,
    * ``std_residual``,
    * ``leverage``,
    * ``cooks_distance``,

  - and a :mod:`pingouin` regression summary table for cross-checking.

* ``run_ch16b_demo(n, random_state)``

  - Simulates the psychology regression dataset,
  - calls :func:`compute_regression_diagnostics`,
  - saves diagnostics and **top influential points** to CSV,
  - generates residuals vs fitted and leverage vs Cook's distance plots,
  - constructs and analyzes Anscombe's Quartet,
  - saves Anscombe summary statistics and plots,
  - prints a concise narrative summary to the console.

* Anscombe helpers (internal names may differ slightly):

  - a function to construct the tidy Anscombe dataset,
  - a function to compute summary statistics by dataset,
  - a plotting function to generate the 2x2 Anscombe scatterplot
    figure with regression lines.

In ``tests/test_psych_ch16b_pingouin_regression_diagnostics.py``:

* One test verifies that diagnostics have the expected columns and that
  leverage behaves as theory predicts (e.g., the average leverage is
  approximately :math:`p / n`, where :math:`p` is the number of
  parameters including the intercept).
* Another test runs :func:`run_ch16b_demo` in a temporary directory and
  verifies that all expected CSV and PNG files exist and are non-empty.
* A third test checks that **Anscombe's Quartet** is implemented
  correctly:

  - there are four datasets with the expected number of rows,
  - group-level summary statistics are nearly identical across datasets,
  - the code produces an Anscombe summary CSV and plot image.

How this Appendix fits into the Track B narrative
=================================================

* Chapter 15 and 15a introduced **correlation** and **partial
  correlation**, using :mod:`pingouin` as a high-level toolbox.
* Chapter 16 developed the core ideas of **linear regression**:
  prediction, least squares, standard error of the estimate, and
  multiple regression.
* Appendix 16a expanded regression with additional estimation examples.
* Appendix 16b (this chapter) emphasizes that

  * even a beautifully written model can be misleading if we ignore
    diagnostics,
  * the *shape* of the data always matters,
  * simple, testable diagnostics can be integrated into every
    analysis pipeline.

By the time students reach Chapter 17 (Mixed-Model Designs), they will
have seen that a PyStatsV1-style analysis is not just about "getting
significant results." It is about building **robust, transparent, and
reproducible** statistical workflows that can be trusted.

Next steps
==========

After completing this appendix, you are ready to move into

* **Chapter 17 – Mixed-Model Designs**, where we combine
  between-subjects and within-subjects factors, and
* later, **Chapter 18 – ANCOVA**, where we explicitly control for
  covariates in more complex models.

In both chapters, the habits you practiced here—**checking assumptions,
visualizing patterns, and treating models as software artifacts**—will
remain central.
