Chapter 16 – Linear Regression
==============================

In Chapter 15 you learned how to quantify relationships between two
variables using correlation. Correlation answers the question:

.. epigraph::

   *"How strongly are two variables associated?"*

Linear regression goes one step further. It answers a different
question:

.. epigraph::

   *"How well can we **predict** one variable from one or more
   other variables?"*

In this chapter you will:

* build the idea of a **line of best fit** for predicting an outcome,
* understand how the **least-squares** method chooses that line,
* interpret the **standard error of the estimate** as typical
  prediction error,
* extend to **multiple regression**, where several predictors work
  together,
* and use :mod:`pystatsv1` and :mod:`pingouin` to fit and interpret
  regression models on a synthetic psychology dataset.


16.1 Prediction: The Line of Best Fit
-------------------------------------

Imagine we want to predict a student's exam score from their number of
study hours. Each student gives us one data point:
``(study_hours, exam_score)``. If we scatter those points, a clear
trend often appears: students who study more tend to score higher.

**Linear regression** summarizes that trend with a straight line:

.. math::

   \widehat{Y} = bX + a

where

* :math:`\widehat{Y}` is the *predicted* value of the outcome,
* :math:`X` is the predictor,
* :math:`b` is the **slope** (how much :math:`Y` changes for a
  one-unit change in :math:`X`), and
* :math:`a` is the **intercept** (the predicted value of :math:`Y`
  when :math:`X = 0`).

In psychology, we often use regression to predict:

* exam performance from study time,
* depressive symptoms from life stress,
* therapy outcomes from baseline severity and treatment type,
* or attention scores from sleep quality and caffeine intake.

The important idea is that regression is a **model of prediction**.
We care both about *how strong* the relationship is and *how well we
can forecast new data*.

Interpretation of the slope
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose our fitted line is

.. math::

   \widehat{\text{Exam Score}} = 5.0 \times \text{Study Hours} + 60.

The slope :math:`b = 5.0` means:

*For every extra hour of study, exam score is predicted to increase by
about 5 points, on average.*

The intercept :math:`a = 60` means:

*A student who studied 0 hours is predicted to score 60 (although we
should be cautious about interpreting predictions far outside the
observed range).*


16.2 Least Squares: Choosing the Best Line
------------------------------------------

There are infinitely many lines we could draw through a cloud of
points. Linear regression chooses the one that minimizes the **sum of
squared residuals**.

A **residual** is the difference between the observed outcome and the
predicted outcome from the line:

.. math::

   e_i = Y_i - \widehat{Y}_i.

The **least-squares** solution chooses :math:`a` and :math:`b` to
minimize

.. math::

   \sum_{i=1}^{n} e_i^2 = \sum_{i=1}^{n} (Y_i - \widehat{Y}_i)^2.

This has several nice properties:

* it gives more weight to large errors (because of squaring),
* it has a closed-form solution (no iterative search is required),
* and it links naturally to the Pearson correlation :math:`r` and
  the ANOVA framework you saw in Chapters 12–14.

In the Chapter 16 lab script we compute the least-squares solution
using both basic NumPy functions and the higher-level
:func:`pingouin.linear_regression` helper for cross-checking.


16.3 Standard Error of the Estimate
-----------------------------------

No regression line predicts perfectly. Different students with the
same study hours will still have different exam scores. The **standard
error of the estimate** summarizes typical prediction error in the
original units of the outcome variable.

After we fit the line, we compute residuals :math:`e_i` for each case
and then:

.. math::

   S_\text{est} = \sqrt{\frac{\sum e_i^2}{n - 2}}.

This is similar to a standard deviation of the residuals. A smaller
:math:`S_\text{est}` means:

* predictions are typically closer to the observed scores,
* the regression line fits the data more tightly,
* and we have more precise forecasts for new cases.

In the lab we will:

* print :math:`S_\text{est}` for our simple regression model,
* compare it across different models,
* and relate it back to the residual plots.


16.4 Multiple Regression and R²
-------------------------------

Real psychological outcomes usually depend on **many** factors at
once. Multiple regression extends the linear model to several
predictors:

.. math::

   \widehat{Y} = b_0 + b_1 X_1 + b_2 X_2 + \dots + b_k X_k.

For example, our synthetic dataset in Chapter 16 includes:

* ``study_hours`` – weekly study time,
* ``sleep_hours`` – average nightly sleep,
* ``stress`` – perceived stress score,
* and ``exam_score`` – exam performance.

A multiple regression model might be:

.. math::

   \widehat{\text{Exam Score}} =
   b_0 + b_1 \times \text{Study Hours}
       + b_2 \times \text{Sleep Hours}
       - b_3 \times \text{Stress}.

Key ideas:

* Each slope :math:`b_j` is a **partial effect**: it tells us how
  much :math:`Y` is expected to change when :math:`X_j` increases by
  one unit, holding the other predictors constant.
* We can assess overall model fit with :math:`R^2`, the proportion of
  variance in :math:`Y` explained by the predictors.
* Adjusted :math:`R^2` penalizes adding predictors that do not really
  help.

In the lab script we use :func:`pingouin.linear_regression` to fit a
multiple regression model with ``exam_score`` as the outcome and
multiple predictors. We then interpret:

* the coefficient signs (which predictors help or hurt),
* their statistical significance (p-values),
* and the overall :math:`R^2` / adjusted :math:`R^2`.


16.5 PyStatsV1 Lab: Building a Predictive Model
-----------------------------------------------

The Chapter 16 lab script is
:mod:`scripts.psych_ch16_regression`. It demonstrates:

* simulating a psychology dataset with exam performance,
* fitting and interpreting a **simple linear regression**,
* fitting a **multiple regression** with several predictors,
* saving results for replication,
* and visualizing the line of best fit.

Overview of the lab script
~~~~~~~~~~~~~~~~~~~~~~~~~~

The script is structured into a few main helper functions:

* :func:`simulate_psych_regression_dataset`

  Creates a synthetic dataset with columns such as
  ``stress``, ``sleep_hours``, ``study_hours``, and ``exam_score``,
  using a known underlying regression model. Because we know the
  "true" slopes, we can check that the estimated values behave as
  expected.

* :func:`fit_simple_regression`

  Fits a simple regression predicting ``exam_score`` from
  ``study_hours``. Returns the slope, intercept, correlation,
  :math:`R^2`, and standard error of the estimate.

* :func:`fit_multiple_regression`

  Uses :func:`pingouin.linear_regression` to fit a multiple regression
  model with several predictors. Returns the regression table along
  with :math:`R^2` and adjusted :math:`R^2` for quick inspection.

* :func:`plot_regression_line`

  Generates a scatterplot of ``study_hours`` versus ``exam_score``
  along with the fitted line. The figure is saved to the
  ``outputs/track_b`` folder for use in slides or assignments.

When you run the script via:

.. code-block:: bash

   make psych-ch16

you will see printed output that includes:

* a preview of the simulated dataset,
* the simple regression slope, intercept, :math:`R^2`, and
  standard error of the estimate,
* the multiple regression summary from :mod:`pingouin`,
* and file paths where the data, table, and figure were saved.


Files written by the lab
~~~~~~~~~~~~~~~~~~~~~~~~~

The script saves three main artifacts:

* ``data/synthetic/psych_ch16_regression.csv``

  The simulated psychology dataset used for all analyses.

* ``outputs/track_b/ch16_regression_summary.csv``

  A CSV file containing the multiple regression summary table
  produced by :func:`pingouin.linear_regression`.

* ``outputs/track_b/ch16_regression_fit.png``

  A scatterplot of study hours and exam scores with the regression
  line superimposed.

These files make it easy to reproduce the main figures and tables
for homework, lecture slides, or exam preparation.


PyStatsV1 and Pingouin together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As in Chapters 14 and 15, we treat :mod:`pingouin` as a
**trusted reference implementation**. Our own helper functions
use NumPy and pandas to compute regression quantities "from scratch",
and then we cross-check key numbers against
:func:`pingouin.linear_regression`.

This dual approach reinforces the core philosophy of PyStatsV1:

.. epigraph::

   *Don't just calculate your results — engineer them.*

By writing small, well-tested functions and validating them against
trusted libraries, students learn both the statistical ideas and the
software engineering mindset needed for reproducible science.


Checklist: What You Should Be Able to Do
----------------------------------------

By the end of Chapter 16, you should be able to:

* explain what the regression line :math:`\widehat{Y} = bX + a` means
  in words,
* interpret the slope and intercept in a psychology example,
* describe how the least-squares method chooses the "best" line,
* compute and interpret the standard error of the estimate,
* explain the difference between simple and multiple regression,
* interpret :math:`R^2` and adjusted :math:`R^2`,
* and run the Chapter 16 PyStatsV1 lab to build and evaluate a
  predictive model.
