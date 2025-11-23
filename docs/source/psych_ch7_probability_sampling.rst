.. _psych_ch7_probability_sampling:

Psychological Science & Statistics – Chapter 7
==============================================

Probability, Sampling, and the Distribution of Sample Means
-----------------------------------------------------------

Up to this point, we have focused on **describing** data:

* Chapter 4: What does the distribution *look* like? (graphs)
* Chapter 5: How can we summarize it with numbers? (center & spread)
* Chapter 6: How can we model it with a **normal distribution** and **z-scores**?

Starting in this chapter, we begin the transition from **description** to
**inference**. We rarely have data for an entire population. Instead, we:

* draw a **sample**,
* compute statistics (like a mean), and
* use those statistics to say something about the population.

To understand why this works, we need three ideas:

1. Basic probability as long-run relative frequency
2. Random sampling from a population
3. The **distribution of sample means** (a sampling distribution)

This chapter provides the conceptual bridge to the inferential procedures you
will encounter in later chapters.

Why Probability?
----------------

In everyday language, "probability" often means "how confident I feel."
In statistics, probability has a more precise interpretation:

*Probability is the long-run relative frequency of an event under repeated
conditions.*

For example, if you flip a fair coin many times, the proportion of heads will
stabilize around 0.5. In the long run:

.. math::

   P(\text{Heads}) = 0.5

We use probabilities in statistics to quantify uncertainty about:

* which sample we might observe,
* how far a sample mean might fall from the population mean,
* and how surprising our data would be if a null hypothesis were true.

Populations, Samples, and Sampling Error
----------------------------------------

A **population** is the full set of individuals or observations we care about.
A **sample** is a subset of that population that we actually measure.

Key ideas:

* The **population mean** (often written :math:`\mu`) is usually unknown.
* The **sample mean** (often written :math:`\bar{x}`) is an estimator of
  :math:`\mu`.
* Different random samples produce different sample means. This variability is
  called **sampling error**.

Sampling error is not a mistake. It is a built-in feature of working with
samples.

Random Sampling
---------------

To keep our reasoning clean, we often assume we have a **random sample**.
Informally, this means:

* Every member of the population has some chance of being included.
* The selection mechanism does not systematically favor certain individuals.

In practice, real psychological samples (e.g., volunteers from a subject pool)
are rarely perfectly random. However, random sampling is a useful *ideal model*
for understanding variability in sample statistics.

The Distribution of Sample Means
--------------------------------

Imagine we could:

1. Start with a large population (or a very large synthetic dataset).
2. Draw many random samples of size :math:`n`.
3. Compute the sample mean for each sample.

If we repeated this process a large number of times and graphed all the sample
means, we would obtain the **sampling distribution of the mean**.

Important properties of the sampling distribution of the mean:

* It is centered near the population mean :math:`\mu`.
* Its spread is given by the **standard error of the mean**:

  .. math::

     \text{SE}_{\bar{X}} = \frac{\sigma}{\sqrt{n}}

* As the sample size :math:`n` increases, the sampling distribution becomes
  narrower (less variable).
* Under broad conditions, the sampling distribution of the mean is
  approximately **normal**, even when the raw data are skewed.

This last point is the heart of the **Central Limit Theorem**.

The Central Limit Theorem (Informal)
------------------------------------

The **Central Limit Theorem (CLT)** can be stated informally as follows:

*If you draw many independent random samples of size :math:`n` from a
population with mean :math:`\mu` and standard deviation :math:`\sigma`, then
for sufficiently large :math:`n`, the distribution of the sample mean
:math:`\bar{x}` will be approximately normal, centered at :math:`\mu`, with
standard deviation :math:`\sigma / \sqrt{n}`.*

This is remarkable because it holds even when the raw data are **not** normal.
For example, reaction times are often positively skewed, but the distribution
of sample means of reaction times can still be quite normal-looking.

In later chapters, the CLT justifies many inferential procedures, including
confidence intervals and hypothesis tests.

PyStatsV1 Lab: Simulating Sampling Distributions
------------------------------------------------

In this lab, you will use PyStatsV1 to build intuition for sampling
distributions:

1. Generate a **synthetic population** of "stress scores" that is skewed
   (not normal).
2. Draw many random samples of size :math:`n` from this population.
3. Compute the sample mean for each sample.
4. Plot:

   * the **population distribution**, and
   * the **distribution of sample means**.

5. Compare their shapes and spreads.
6. Relate the observed spread of sample means to the idea of
   **standard error**.

All code for this lab lives in:

* ``scripts/sim_psych_ch7_sampling.py``

and it will write outputs to:

* ``data/synthetic/psych_ch7_population_stress.csv`` (population)
* ``data/synthetic/psych_ch7_sample_means.csv`` (sample means)
* ``outputs/track_b/ch07_population_vs_sample_means.png`` (plot)

Running the Lab Script
~~~~~~~~~~~~~~~~~~~~~~

From the project root, you can run the Chapter 7 lab script directly:

.. code-block:: bash

   python -m scripts.sim_psych_ch7_sampling

If you prefer to use ``make`` and your Makefile defines the convenience target,
you can run:

.. code-block:: bash

   make psych-ch07

This will:

* Generate a large synthetic population of "stress scores"
* Draw many random samples of size :math:`n`
* Compute the sample mean for each sample
* Save the population and sample means to CSV files
* Produce a plot comparing the population distribution and the sampling
  distribution of the mean
* Print summary information to the console

Expected Console Output
~~~~~~~~~~~~~~~~~~~~~~~

Your exact numbers may vary slightly depending on configuration, but you
should see output similar to:

::

   Generated population with 50000 individuals
   Population mean stress_score = 19.98
   Population SD   stress_score = 9.95

   Drew 1000 samples of size n = 25
   Sampling distribution mean = 20.02
   Sampling distribution SD   = 2.02 (theoretical SE ≈ 1.99)

   Wrote population to: data/synthetic/psych_ch7_population_stress.csv
   Wrote sample means to: data/synthetic/psych_ch7_sample_means.csv
   Wrote plot to: outputs/track_b/ch07_population_vs_sample_means.png

Interpreting the Plot
~~~~~~~~~~~~~~~~~~~~~

The script produces a figure with two histograms:

1. The **population distribution** of ``stress_score``:
   * typically skewed to the right (more low-to-moderate scores, fewer high
     scores).
2. The **sampling distribution of the mean** (sample means):
   * much less skewed,
   * more bell-shaped,
   * and noticeably narrower (less variable).

Questions to consider:

* How does the shape of the sample means compare to the shape of the
  population?
* Why is the distribution of sample means narrower?
* How does the observed SD of the sample means compare to the theoretical
  standard error :math:`\sigma / \sqrt{n}`?

Your Turn: Experiments with Sample Size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try modifying the script (or using function arguments, if exposed) to explore:

1. **Different sample sizes**  
   Compare ``n = 5``, ``n = 25``, and ``n = 100``.  
   How does the spread of the sampling distribution change?

2. **Number of replications**  
   Increase the number of samples (e.g., from 200 to 2000).  
   Does the sampling distribution look smoother?  
   Does the observed SD of the sample means get closer to the theoretical
   standard error?

3. **Different population shapes**  
   Experiment with different population-generating mechanisms (e.g., less
   skewed vs. more skewed distributions).  
   How does this affect the sampling distribution for small vs. large
   sample sizes?

Summary
-------

In this chapter you learned how:

* Probability can be interpreted as long-run relative frequency.
* Samples differ from populations due to **sampling error**.
* The **sampling distribution of the mean** is centered at the population
  mean and becomes less variable as the sample size increases.
* Under broad conditions, the sampling distribution of the mean is
  approximately normal (the **Central Limit Theorem**).
* Simulation can make these abstract ideas concrete and visual.

These ideas are the backbone of the inferential tools in later chapters:

* Hypothesis testing (Chapter 8)
* The one-sample t-test (Chapter 9)
* Confidence intervals for means
* And more advanced models in later chapters

Next Steps
----------

In Chapter 8, we will build on these ideas to introduce the logic of
**null hypothesis significance testing (NHST)**, using probability to decide
whether an observed sample is "surprising" under a particular null model.
