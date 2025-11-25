.. _psych_ch9_one_sample_ci:

Psychological Science & Statistics – Chapter 9
==============================================

The One-Sample t-Test and Confidence Intervals
----------------------------------------------

In Chapter 8 you learned the *logic* of hypothesis testing using a simulation-
based one-sample **t-test**. You saw how to:

* state a null hypothesis,
* compute a sample t-statistic,
* build a null distribution of t-values under :math:`H_0`, and
* approximate a p-value by checking how extreme :math:`t_\text{obs}` is.

In this chapter we take the next step: the *analytic* (formula-based) one-sample
t-test, and the closely related **95% confidence interval** (CI) for a population
mean.

This chapter connects the simulation-based intuition from Chapter 8 to the
classical t-test formulas used throughout psychological science.

When to Use a One-Sample t-Test
-------------------------------

Use a **one-sample t-test** when you want to compare a sample mean to a
known or hypothesized population mean:

*Does the population of students represented by this class have a mean stress score of 20?*

Mathematically, the hypotheses are:

.. math::

   H_0: \mu = \mu_0 \\
   H_1: \mu \ne \mu_0

Why We Use t (Instead of z)
---------------------------

When the population standard deviation :math:`\sigma` is unknown—as is
almost always the case in psychology—we use the **sample standard
deviation** :math:`s`. Substituting :math:`s` introduces extra uncertainty,
leading to a **t distribution** instead of a normal distribution.

The estimated standard error is:

.. math::

   SE = \frac{s}{\sqrt{n}}

The t-statistic is:

.. math::

   t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}}

Confidence Intervals
--------------------

A **95% confidence interval** around a mean provides a range of plausible
population values:

.. math::

   \bar{x} \pm t^* \frac{s}{\sqrt{n}}

where :math:`t^*` is the critical value from the t distribution with
:math:`n-1` degrees of freedom.

Interpretation:

*If we repeated the study many times, 95% of the resulting CIs would contain the
true population mean.*

Connecting Confidence Intervals and Hypothesis Tests
----------------------------------------------------

A powerful insight:

*If the 95% CI **does not include** :math:`\mu_0`, the two-sided t-test will
reject :math:`H_0` at :math:`\alpha = 0.05`.*

*If the CI **includes** :math:`\mu_0`, the t-test will fail to reject :math:`H_0`.*

PyStatsV1 Lab: A One-Sample t-Test With Confidence Intervals
------------------------------------------------------------

In this lab, you will:

1. Load a synthetic population of stress scores (same population used in Ch. 7–8).
2. Draw a random sample of size :math:`n`.
3. Compute:

   * sample mean :math:`\bar{x}`,
   * sample SD :math:`s`,
   * standard error :math:`SE`,
   * t-statistic,
   * degrees of freedom :math:`df = n-1`,
   * p-value (analytic),
   * 95% confidence interval.

4. Compare:

   * the analytic t-test,
   * the 95% CI,
   * and (optionally) the simulation results from Chapter 8.

All code for this chapter lives in:

``scripts/psych_ch9_one_sample_ci.py``

Running the Lab Script
~~~~~~~~~~~~~~~~~~~~~~

From the project root:

.. code-block:: bash

   python -m scripts.psych_ch9_one_sample_ci

If you have a Makefile target:

.. code-block:: bash

   make psych-ch09

Expected Console Output
~~~~~~~~~~~~~~~~~~~~~~~

Your numbers will vary due to randomness, but output will look similar to:

::

   Loaded synthetic population with 50000 individuals
   Population mean stress_score = 19.98
   Population SD   stress_score = 9.94

   Drawn sample size n = 25
   Sample mean = 22.10
   Sample SD   = 10.44
   SE          = 2.09
   t statistic = 1.01
   df          = 24

   Analytic two-sided p-value = 0.323
   95% CI = [17.80, 26.40]

Interpreting Your Output
~~~~~~~~~~~~~~~~~~~~~~~~

Focus on:

* the **t-statistic**: How many standard errors your mean is from the null;
* the **p-value**: Is the result “rare” under :math:`H_0`?
* the **CI**: Does the interval contain the hypothesized value :math:`\mu_0`?

Your Turn: Practice
~~~~~~~~~~~~~~~~~~~

1. **Change the null value** :math:`\mu_0` and observe how the t-statistic changes.
2. **Change the sample size** :math:`n` and see how the CI narrows or widens.
3. **Run the analysis multiple times** to see sampling variability.

Summary
-------

In this chapter you learned:

* the formula-based one-sample t-test,
* how to compute a 95% confidence interval,
* the connection between CIs and hypothesis tests.

In the next chapter (Chapter 10) we extend this logic to comparing
**two independent groups** using the independent-samples t-test.
