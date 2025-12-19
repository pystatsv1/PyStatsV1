Track C – Chapter 19 Problem Set (Non-Parametric Statistics)
============================================================

This problem set practices the core ideas of **non-parametric statistics** and **chi-square tests**:

- When assumptions fail (non-normality, ordinal data, heavy skew, outliers)
- Categorical outcomes (counts and contingency tables)

You will practice:

1. **Chi-square goodness-of-fit** (does the observed distribution match an expected one?)
2. **Chi-square independence** (are two categorical variables related?)
3. **Mann–Whitney U** (2-group alternative to the independent t-test)
4. **Kruskal–Wallis** (k-group alternative to one-way ANOVA)

Run the worked solutions
------------------------

.. code-block:: bash

   make psych-ch19-problems

Run only the tests
------------------

.. code-block:: bash

   make test-psych-ch19-problems

Files and outputs
-----------------

The solution script writes:

- Synthetic datasets: ``data/synthetic/``
- Summaries + plots: ``outputs/track_c/``

Exercises
---------

Exercise 1 — Chi-square goodness-of-fit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A 4-category variable is sampled. The expected distribution is uniform,
but the observed counts are biased. You should see a significant GOF test.

Exercise 2 — Chi-square independence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two categorical variables (``condition`` and ``outcome``) are associated.
You should see a significant chi-square test of independence and a non-trivial effect size.

Exercise 3 — Mann–Whitney U and Kruskal–Wallis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Skewed (lognormal) data are generated for groups A, B, and C.
You should see:

- a significant **Mann–Whitney U** difference between A and B
- a significant **Kruskal–Wallis** difference across A, B, and C
