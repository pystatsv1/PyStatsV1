
Chapter 16a Appendix: Linear Regression with Pingouin
=====================================================

Motivation
----------

In :doc:`psych_ch16_regression`, you learned how to:

- Simulate a psychology dataset with several predictors
- Fit a simple linear regression by hand (using NumPy)
- Fit a multiple regression model
- Interpret the slope, intercept, :math:`R^2`, and standard error of the estimate

In this appendix, we lean more heavily on the :mod:`pingouin` library to
engineer regression analyses as *re-usable, testable components*.

Why Pingouin for regression?
----------------------------

Pingouin is a Python 3 statistics library built on top of NumPy and pandas.
For regression, :func:`pingouin.linear_regression` gives you, in a single
DataFrame:

- Unstandardized coefficients (``coef``)
- Standard errors (``se``)
- t-statistics (``T``) and p-values (``pval``)
- Model-level :math:`R^2` and adjusted :math:`R^2`
- Confidence intervals for each coefficient

This pairs naturally with the PyStatsV1 philosophy:

    *Don't just calculate your results — engineer them.*

Instead of copying numbers from an output window into a homework sheet, we
write small, well-tested scripts that can be re-run, inspected and adapted
to new research projects.

Overview of the 16a lab
-----------------------

The 16a appendix is powered by the script:

.. code-block:: bash

   python -m scripts.psych_ch16a_pingouin_regression_demo

It reuses the same simulated dataset generator introduced in Chapter 16:

.. code-block:: python

   from scripts.psych_ch16_regression import simulate_psych_regression_dataset

and then uses :mod:`pingouin` to:

1. Fit a *multiple regression* model

   .. math::
      \text{exam\_score} = b_0 + b_1 \times \text{study\_hours}
                               + b_2 \times \text{sleep\_hours}
                               + b_3 \times \text{stress}
                               + b_4 \times \text{motivation} + e

2. Compute *standardized* regression coefficients (betas) by running the same
   model on z-scored variables.

3. Extract *partial effects* using :func:`pingouin.partial_corr`, so students
   can see how a predictor relates to the outcome after controlling for other
   variables.

The goal is not to introduce a brand-new design, but to show how the
*measurement model* from Chapter 16 behaves when we add a professional
regression toolbox on top.

Section 16a.1 – Recap: Why multiple regression?
-----------------------------------------------

In Chapter 16, we motivated multiple regression as an extension of correlation:

- Correlation: how two variables move together
- Regression: how we *predict* one variable from one (simple) or many
  (multiple) predictors

Multiple regression helps us answer questions like:

- "How many points of exam score do we gain for each extra hour of study,
  **holding sleep constant**?"
- "Is the effect of sleep on exam performance still present after controlling
  for stress and motivation?"

This language ("holding constant") maps directly onto partial regression and
partial correlation. Pingouin makes those quantities easy to compute.

Section 16a.2 – Pingouin's linear_regression
--------------------------------------------

The core workhorse in this appendix is
:func:`pingouin.linear_regression`. Its minimal usage pattern looks like:

.. code-block:: python

   import pingouin as pg

   X = df[["study_hours", "sleep_hours", "stress", "motivation"]]
   y = df["exam_score"]

   reg_table = pg.linear_regression(X=X, y=y)

The returned ``reg_table`` is a pandas DataFrame with one row per term
(intercept and predictors). Key columns include:

- ``names`` – the name of the predictor (or ``Intercept``)
- ``coef`` – the unstandardized regression coefficient
- ``se`` – standard error of the coefficient
- ``T`` – t-statistic (coefficient divided by its standard error)
- ``pval`` – p-value for a two-sided test of :math:`H_0: b_i = 0`
- ``r2`` – model :math:`R^2` (repeated on each row)
- ``adj_r2`` – adjusted :math:`R^2`

In :mod:`scripts.psych_ch16a_pingouin_regression_demo`, we wrap this logic
into a helper function so that it can be imported and tested:

.. code-block:: python

   from scripts.psych_ch16_regression import simulate_psych_regression_dataset
   import pingouin as pg

   def build_pingouin_regression_tables(df):
       X = df[["study_hours", "sleep_hours", "stress", "motivation"]]
       y = df["exam_score"]
       raw_table = pg.linear_regression(X=X, y=y)
       # (plus a standardized version, see next section)
       ...

This also means that future chapters (e.g., ANCOVA or mixed models) could
reuse the same simulation code and regression helpers for more advanced demos.

Section 16a.3 – Standardized coefficients (betas)
-------------------------------------------------

Unstandardized coefficients (e.g., ``+4 points per extra study hour``) are
often the most intuitive for reporting. However, standardized coefficients
("betas") can be helpful when predictors are on very different scales.

To obtain standardized coefficients, we simply:

1. Z-score the predictors and the outcome.
2. Run :func:`pingouin.linear_regression` on the standardized variables.
3. Interpret the resulting ``coef`` values as *change in standard deviations
   of the outcome per one standard deviation change in the predictor*.

In the 16a script we perform this transformation with:

.. code-block:: python

   def zscore_columns(df, columns):
       zdf = df.copy()
       for col in columns:
           col_mean = zdf[col].mean()
           col_std = zdf[col].std(ddof=0)
           zdf[col + "_z"] = (zdf[col] - col_mean) / col_std
       return zdf

   zdf = zscore_columns(
       df,
       ["exam_score", "study_hours", "sleep_hours", "stress", "motivation"],
   )

We then fit a second regression model:

.. code-block:: python

   X_z = zdf[["study_hours_z", "sleep_hours_z", "stress_z", "motivation_z"]]
   y_z = zdf["exam_score_z"]

   standardized_table = pg.linear_regression(X=X_z, y=y_z)

The resulting ``standardized_table`` is saved to
``outputs/track_b/ch16a_regression_standardized.csv`` and printed to the
console so students can compare unstandardized and standardized effect sizes.

Section 16a.4 – Partial effects and partial correlation
-------------------------------------------------------

In a multiple regression, each coefficient is a *partial effect*: it describes
the association between that predictor and the outcome *after controlling for*
(all else equal to) the other predictors in the model.

Pingouin also exposes these partial relationships directly via
:func:`pingouin.partial_corr`, which computes partial correlation
coefficients.

For example, to examine the relationship between exam score and study hours
while controlling for stress and motivation, the 16a script uses:

.. code-block:: python

   partial = pg.partial_corr(
       data=df,
       x="study_hours",
       y="exam_score",
       covar=["stress", "motivation"],
       method="pearson",
   )

The resulting DataFrame contains:

- ``r`` – the partial correlation coefficient
- ``CI95%`` – a confidence interval for the partial correlation
- ``p-val`` – a p-value testing :math:`H_0: \rho_{xy \cdot \text{covar}} = 0`

The key conceptual link for students is:

- The *sign* and *relative magnitude* of the partial correlation
  align with the regression coefficient for that predictor.
- The partial correlation can be interpreted in the same "holding other
  variables constant" language used to explain multiple regression.

Section 16a.5 – Running the 16a lab
-----------------------------------

The appendix demo is designed to run from the command line and to save its
artifacts into the same folder structure as the other Track B labs.

From the root of the repository, with the virtual environment activated:

.. code-block:: bash

   # Run the demo script (regression + partial correlations)
   make psych-ch16a

   # Or directly via Python
   python -m scripts.psych_ch16a_pingouin_regression_demo

   # Run the tests for this chapter's appendix
   make test-psych-ch16a

   # Inspect all outputs under:
   # - data/synthetic/psych_ch16_regression.csv
   # - outputs/track_b/ch16a_regression_raw.csv
   # - outputs/track_b/ch16a_regression_standardized.csv
   # - outputs/track_b/ch16a_partial_corr_exam_study.csv

The associated test module,
:mod:`tests.test_psych_ch16a_pingouin_regression_demo`, checks that:

- The regression tables contain the expected columns.
- Study hours and sleep hours have positive regression coefficients.
- Stress has a negative regression coefficient.
- The partial correlation between exam score and study hours (controlling
  for stress and motivation) is positive and statistically significant.

These tests turn the 16a appendix into *executable documentation* for
both students and instructors.

Section 16a.6 – For instructors
-------------------------------

Some suggestions for using this appendix in teaching:

- **Compare models in class.** Run the Chapter 16 lab and the 16a Pingouin
  appendix side-by-side. Ask students to reconcile the manual calculations
  with the Pingouin output.

- **Highlight effect sizes.** Use the standardized regression table to
  discuss which predictors have the strongest relative influence on exam
  performance.

- **Discuss collinearity.** Because predictors like study hours, sleep,
  stress, and motivation are correlated with each other, multiple regression
  is a natural context to introduce collinearity and its consequences.

- **Encourage replication.** Invite students to fork the PyStatsV1 repo,
  modify the simulation parameters (e.g., make sleep more important), and
  observe how the Pingouin tables change.

In later chapters (e.g., ANCOVA, mixed-model designs), we can revisit this
dataset and the Pingouin regression helpers as a familiar sandbox for more
advanced modeling.
