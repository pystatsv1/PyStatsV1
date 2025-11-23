.. _psych_ch6_normal_zscores:

Psychological Science & Statistics – Chapter 6
==============================================

The Normal Distribution and z-Scores
------------------------------------

In Chapters 4 and 5 you learned how to *describe* a distribution using graphs
(histograms, frequency polygons) and summary statistics (mean, median, variance,
standard deviation). These tools help us understand what our data *look like*.

In this chapter we take an important next step: we introduce the **normal
distribution**, a mathematical model used throughout psychology and statistical
inference. The normal distribution helps us:

* compare individual scores to a reference population,
* identify “unusual” observations,
* standardize variables measured on different scales, and
* compute probabilities, percentiles, and standardized effect sizes.

We will use the same synthetic sleep-study dataset introduced earlier
(:ref:`psych_sleep_regen_note`) and learn how to:

* Fit a normal model to a single variable
* Convert raw scores to **z-scores**
* Interpret where an individual score falls in a distribution
* Visualize empirical data alongside a theoretical normal curve
* Compute simple probabilities under the normal model

A Statistical Clarification: Raw Data vs. Sampling Distributions
----------------------------------------------------------------

It is important to distinguish between:

1. **The distribution of raw scores**, which may or may not be normal  
   (e.g., reaction times are usually positively skewed), and

2. **The distribution of sample means**, which *is* approximately normal under
   broad conditions, by the Central Limit Theorem (CLT).

Even when raw observations are skewed, the *sample mean* has an approximately
normal distribution when the sample size is large enough. If the parent population is Normal then for small samples,
the standardized (using the sample standard deviation) sample mean follows a **Student’s t distribution**, not a
normal distribution.

In this chapter, we focus on **z-scores for individual observations**, a tool
commonly used in psychological measurement. Later chapters (especially Chapter 7
and Chapter 9) introduce sampling distributions, the CLT, and the t distribution
in more depth.

The Normal Distribution: A Workhorse in Applied Statistics
--------------------------------------------------

The normal distribution (also called the *Gaussian* or *bell curve*) is one of
the most important models in psychological science and applied statistics. Many aggregated or
psychometrically smoothed variables are approximately ("close enough") normal or can be modeled as normal in appropriate scenarios. For example:

* IQ scores (by design)
* Composite cognitive performance scores
* Height and weight
* Many Likert-scale *sum scores*
* Measurement error under many conditions

A normal distribution is defined by only two parameters:

* The **mean** (center)
* The **standard deviation** (spread)

Once these two numbers are known, we can describe the *entire* distribution
mathematically.

Standardizing: From Raw Scores to z-Scores
------------------------------------------

A **z-score** expresses a raw score in standard deviation units:

.. math::

   z = \\frac{X - \\mu}{\\sigma}


When population parameters are unknown (as is typical), we substitute sample estimates.

Interpreting z-scores (where average = mean):

* ``z = 0`` → Exactly average  
* ``z = +1`` → One standard deviation above average  
* ``z = -2`` → Two standard deviations below average  
* ``z = +2`` → Approximately the 97.5th percentile (under the normal model)

In psychology, z-scores are useful because they make variables comparable even
when measured on different scales.

Examples:

* ``sleep_hours_z = -1.2``  
  The participant slept *less* than average (mean) by 1.2 SDs.

* ``reaction_time_z = +0.8``  
  The participant was *slower* than the mean (higher RTs → slower responses).

In this chapter’s PyStatsV1 lab, you will compute z-scores using empirical
summary statistics (sample mean and sample standard deviation). This is a common
practice when working with real psychological data.

PyStatsV1 Lab: Normal Distribution and z-Scores
-----------------------------------------------

In this lab, you will:

1. Load the sleep-study dataset
2. Compute z-scores for one continuous variable (e.g., ``sleep_hours``)
3. Generate a histogram overlaid with a normal density curve
4. Inspect the distribution of z-scores
5. Compute simple probabilities using a normal model

Remember: the normal curve is a *model*. The empirical data do not need to be
perfectly normal in order for z-scores to be meaningful or useful.

All code for this chapter lives in:

``scripts/psych_ch6_normal_zscores.py``

and the dataset lives in:

``data/synthetic/psych_sleep_study.csv``

See :ref:`psych_sleep_regen_note` if you need to regenerate the dataset.

Running the Lab Script
~~~~~~~~~~~~~~~~~~~~~~

From the project root, run:

.. code-block:: bash

   python -m scripts.psych_ch6_normal_zscores

Or, if using the Makefile target:

.. code-block:: bash

   make psych-ch06

This will:

* Load the sleep-study dataset
* Compute the sample mean, sample standard deviation, and corresponding z-scores
* Generate a histogram overlaid with a fitted normal curve
* Print summary information to the console
* Save a PNG of the plot (depending on your local settings)

Expected Console Output
~~~~~~~~~~~~~~~~~~~~~~~

Numbers may vary slightly depending on random seed and sample size:

::

   Loaded dataset with 200 participants
   sleep_hours mean = 6.98
   sleep_hours SD   = 1.02
   First five z-scores:
       Participant 0:  0.13
       Participant 1: -0.87
       Participant 2:  1.10
       Participant 3: -0.05
       Participant 4:  0.44

Interpreting the Plot
~~~~~~~~~~~~~~~~~~~~~

The figure shows a histogram of ``sleep_hours`` and a fitted normal curve.

Questions to consider:

* Does the empirical distribution appear approximately normal?  
* Are there signs of skewness or kurtosis?  
* Would the normal model be a reasonable approximation?  

Remember that many psychological variables are only *approximately* normal, and
some (like reaction times) are typically skewed.

Your Turn: Practice Interpreting z-Scores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Identify two typical sleepers.**  
   Look for participants with z-scores near ``0``.  
   What does this tell you?

2. **Identify one unusually high value.**  
   Find a participant with ``z > 2``.  
   What percentile does this correspond to?

3. **Identify one unusually low value.**  
   Find a participant with ``z < -2``.  
   What might explain such low sleep values?

4. **Estimate simple probabilities.**  
   Using the normal model, estimate:

   * ``P(Z > 1)``
   * ``P(-1 < Z < 1)``
   * ``P(Z < -2)``

   How close are these to the 68–95–99.7 rule?

Optional Extension: Reaction Times
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try computing and visualizing z-scores for:

``reaction_time_ms``

Questions:

* Are reaction times normally distributed?  
* Are they positively skewed?  
* What happens if you apply a log-transform before standardizing?  

Summary
-------

In this chapter you learned how to:

* Model a psychological variable using a **normal distribution**
* Compute and interpret **z-scores**
* Overlay a theoretical normal curve on empirical data
* Estimate probabilities and percentiles under the normal model
* Distinguish between raw-score distributions and sampling distributions

These tools prepare you for:

* Sampling distributions (Chapter 7)
* Hypothesis testing and the t distribution (Chapter 8)
* The one-sample t-test (Chapter 9)

Next Steps
----------

In Chapter 7, you will learn how probability and sampling work together to form
the basis of **statistical inference**, including why the sample mean becomes
approximately normal even when the raw data are not.
