Chapter 12 – One-Way Analysis of Variance (ANOVA)
=================================================

In Chapters 8–11 you learned how to compare **one** mean (one-sample *t*) and
**two** means (independent and paired-samples *t*).

In this chapter we take the next step: comparing **three or more groups** in a
single experiment. The standard tool is the **one-way analysis of variance
(ANOVA)**.

Typical psychology examples include:

* three therapy conditions (for example, control, CBT, mindfulness),
* four study strategies (rereading, highlighting, practice testing, mixed), or
* multiple dose levels of a drug.

Our goals are to help you:

* understand why simply running many *t*-tests is a bad idea (inflated
  Type I error),
* see how ANOVA **partitions variance** into between-groups and within-groups
  components,
* interpret the *F*-ratio as a signal-to-noise statistic,
* understand why we need **post-hoc tests** when *F* is significant, and
* run a one-way ANOVA and simple Bonferroni-corrected post-hoc tests using
  PyStatsV1.

The Problem with Multiple *t*-Tests
-----------------------------------

Suppose a clinical psychologist compares stress scores across **three
conditions**:

* control (no treatment),
* CBT training, and
* mindfulness training.

A naïve approach is to run a separate independent-samples *t*-test for each
pair:

* control vs. CBT,
* control vs. mindfulness,
* CBT vs. mindfulness.

That is **three** tests. If each test uses :math:`\alpha = 0.05`, what is the
chance of making **at least one** Type I error (false positive) across all
three tests, *even if all population means are equal*?

If each test has a 0.05 chance of a false positive and we (roughly) treat them
as independent, then the chance of **no** Type I errors is

.. math::

   P(\text{no false positives}) \approx (1 - 0.05)^3 = 0.95^3 \approx 0.86.

So the chance of **at least one** false positive is about:

.. math::

   P(\text{at least one false positive})
   \approx 1 - 0.86 = 0.14.

Instead of a 5% family-wise error rate, we are now closer to **14%**. As the
number of groups grows, the number of pairwise tests grows quickly and the
family-wise error rate can become unacceptably large.

The core idea of ANOVA is:

    Rather than doing many separate *t*-tests, we perform **one overall test**
    of the null hypothesis that all group means are equal.

If that global test is significant, we then follow up with more targeted
comparisons (post-hoc tests) using methods that control the overall error rate.

Partitioning Variance: Between-Groups vs. Within-Groups
-------------------------------------------------------

ANOVA works by **partitioning** the total variability in the data into two
parts:

* variability **between groups** (how far the group means are spread out), and
* variability **within groups** (how spread out the scores are inside each
  group).

Let:

* :math:`k` be the number of groups,
* :math:`N` be the total sample size (sum of all group sizes),
* :math:`\bar{X}_j` be the mean of group :math:`j`,
* :math:`n_j` be the sample size in group :math:`j`, and
* :math:`\bar{X}` be the **grand mean** across all participants.

Total Sum of Squares
~~~~~~~~~~~~~~~~~~~~

The total variability around the grand mean is:

.. math::

   SS_{\text{Total}} =
   \sum_{j=1}^{k}\sum_{i=1}^{n_j} (X_{ij} - \bar{X})^2.

Between-Groups Sum of Squares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The between-groups (or treatment) sum of squares measures how far the
**group means** are from the grand mean, weighted by group size:

.. math::

   SS_{\text{Between}} =
   \sum_{j=1}^{k} n_j (\bar{X}_j - \bar{X})^2.

Within-Groups Sum of Squares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The within-groups (or error) sum of squares measures how spread out the scores
are **inside** each group:

.. math::

   SS_{\text{Within}} =
   \sum_{j=1}^{k} \sum_{i=1}^{n_j} (X_{ij} - \bar{X}_j)^2.

These pieces satisfy the key identity:

.. math::

   SS_{\text{Total}} = SS_{\text{Between}} + SS_{\text{Within}}.

Degrees of Freedom
~~~~~~~~~~~~~~~~~~

Each sum of squares has associated degrees of freedom (df):

* Between groups:

  .. math::

     df_{\text{Between}} = k - 1.

* Within groups:

  .. math::

     df_{\text{Within}} = N - k.

* Total:

  .. math::

     df_{\text{Total}} = N - 1.

Mean Squares
~~~~~~~~~~~~

ANOVA converts sums of squares to **mean squares** by dividing by their degrees
of freedom:

.. math::

   MS_{\text{Between}} =
   \frac{SS_{\text{Between}}}{df_{\text{Between}}},

.. math::

   MS_{\text{Within}} =
   \frac{SS_{\text{Within}}}{df_{\text{Within}}}.

* :math:`MS_{\text{Within}}` is an estimate of the population variance based
  on within-group variability.
* If the null hypothesis is true, :math:`MS_{\text{Between}}` is also an
  estimate of the same variance (plus tiny sampling noise).
* If the group means really differ, :math:`MS_{\text{Between}}` becomes
  **larger** than :math:`MS_{\text{Within}}`.

The *F*-Ratio: Signal-to-Noise Logic
------------------------------------

The ANOVA test statistic is the **F-ratio**:

.. math::

   F =
   \frac{MS_{\text{Between}}}{MS_{\text{Within}}}.

This has the **same basic logic** as the *t*-tests you have seen:

* The **numerator** reflects systematic differences between group means
  (signal).
* The **denominator** reflects unsystematic variability within groups (noise).

When all population means are equal, the expected values of
:math:`MS_{\text{Between}}` and :math:`MS_{\text{Within}}` are the same, so
:math:`F` tends to be near 1. As the group means separate, the numerator grows
relative to the denominator and :math:`F` becomes larger than 1.

Under the null hypothesis that all population means are equal,

.. math::

   H_0 : \mu_1 = \mu_2 = \dots = \mu_k,

the *F*-statistic follows an **F distribution** with

* :math:`df_1 = df_{\text{Between}} = k - 1`,
* :math:`df_2 = df_{\text{Within}} = N - k`.

For a right-tailed test, the *p*-value is:

.. math::

   p = P\bigl(F_{df_1, df_2} \ge F_{\text{obs}}\bigr).

If :math:`p < \alpha` (for example, 0.05), we reject :math:`H_0` and conclude
that **at least one** group mean differs from the others.

.. admonition:: Professional Tip: Assumptions Matter

   The standard ANOVA F-test assumes that all groups have roughly **equal
   variances** (homogeneity of variance).

   When sample sizes are unequal and group variances differ a lot, the
   classical F-test can be misleading. In professional research,
   statisticians often check this assumption (for example, using **Levene’s
   test**) and may switch to a robust alternative called **Welch’s ANOVA** if
   the assumption is badly violated.

   In this chapter we focus on the classical, equal-variance version for
   clarity. Later, when you read research articles, pay attention to how
   authors check (or ignore) this assumption.

Effect Size: :math:`\eta^2`
---------------------------

As with *t*-tests, statistical significance does not tell us how large an
effect is. A simple effect size for one-way ANOVA is **eta-squared**:

.. math::

   \eta^2 =
   \frac{SS_{\text{Between}}}{SS_{\text{Total}}}.

Interpretation:

* :math:`\eta^2` represents the **proportion of total variance** in the
  dependent variable that can be attributed to group membership.
* Values range from 0 to 1, with higher values indicating a stronger
  relationship between the grouping factor and the outcome.

Very rough guidelines:

* :math:`\eta^2 \approx 0.01` – small effect
* :math:`\eta^2 \approx 0.06` – medium effect
* :math:`\eta^2 \approx 0.14` – large effect

.. note::

   :math:`\eta^2` is a descriptive statistic for the *sample*. It tends to
   slightly **overestimate** the effect size in the *population*, especially
   with small samples. Advanced researchers often use a corrected measure
   called **omega-squared** (:math:`\omega^2`) for less biased estimates, but
   :math:`\eta^2` is a standard and useful starting point for introductory
   ANOVA.

Post-Hoc Tests: Where Is the Difference?
----------------------------------------

A significant ANOVA tells you that not all means are equal, but it does **not**
tell you which pairs of groups differ.

For our three-condition example, a significant *F* might reflect:

* CBT < control, mindfulness < control, and CBT ≈ mindfulness,
* or CBT < mindfulness, but both similar to control,
* or some other pattern.

To answer "Where is the difference?" we use **post-hoc tests** (or planned
contrasts). These tests compare specific means while controlling the overall
(Type I) error rate.

Two common approaches are:

* **Tukey’s Honestly Significant Difference (HSD)**

  * Uses a special distribution (studentized range) tailored to all pairwise
    comparisons.
  * Controls the family-wise error rate at :math:`\alpha` across all pairs.
  * Widely used default in many statistical packages.

* **Bonferroni correction**

  * Very simple:
    - Decide on the number of comparisons :math:`m`.
    - Use a per-comparison alpha of :math:`\alpha / m`, or equivalently
      multiply each *p*-value by :math:`m` and compare to :math:`\alpha`.
  * Conservative but easy to explain and implement.

In the PyStatsV1 Chapter 12 lab we use **Bonferroni-corrected pairwise
*t*-tests** so that you can see:

* the connection to the Chapter 10 independent-samples *t*-test, and
* how the correction keeps the family-wise error rate under control.

PyStatsV1 Lab: One-Way ANOVA on Stress Scores
---------------------------------------------

In this lab, you will analyze a synthetic experiment in which students are
randomly assigned to one of **three** conditions:

* ``control`` – no stress-management training,
* ``cbt`` – a brief cognitive-behavioral training module,
* ``mindfulness`` – a brief mindfulness training module.

The outcome variable is a continuous ``stress_score`` similar to earlier
chapters.

You will:

* simulate a dataset with stress scores for all three groups,
* compute:

  - group means and sample sizes,
  - :math:`SS_{\text{Between}}`, :math:`SS_{\text{Within}}`,
    :math:`SS_{\text{Total}}`,
  - :math:`MS_{\text{Between}}`, :math:`MS_{\text{Within}}`,
  - the *F*-statistic and its *p*-value,
  - :math:`\eta^2` as an effect size,

* perform Bonferroni-corrected pairwise *t*-tests between the three groups,
* cross-check your ANOVA results against SciPy’s ``f_oneway`` as a
  **safety check**.

All code for this lab lives in:

* ``scripts/psych_ch12_one_way_anova.py``

and the script can optionally write outputs to:

* ``data/synthetic/psych_ch12_one_way_stress.csv``

Running the Lab Script
----------------------

From the project root, you can run:

.. code-block:: bash

   python -m scripts.psych_ch12_one_way_anova

If your Makefile defines a convenience target, you can instead run:

.. code-block:: bash

   make psych-ch12

This will:

* simulate a one-way between-subjects dataset with three groups (for example,
  30 participants per group),
* compute the one-way ANOVA table:

  - :math:`SS_{\text{Between}}`, :math:`df_{\text{Between}}`,
    :math:`MS_{\text{Between}}`,
  - :math:`SS_{\text{Within}}`, :math:`df_{\text{Within}}`,
    :math:`MS_{\text{Within}}`,
  - *F*, *p*, and :math:`\eta^2`,

* print the group means and sample sizes,
* run pairwise independent-samples *t*-tests for:

  - control vs. cbt,
  - control vs. mindfulness,
  - cbt vs. mindfulness,

  and report both uncorrected *p*-values and Bonferroni-adjusted
  *p*-values,

* cross-check against SciPy’s built-in ``f_oneway`` and warn if the values
  disagree beyond tiny numerical differences,
* optionally save the simulated dataset as a CSV file for further exploration.

Expected Console Output
-----------------------

Your exact numbers will vary if you change the seed or parameters, but with the
default settings you will see something like:

.. code-block:: text

   One-way ANOVA on stress scores (control vs CBT vs mindfulness)
   --------------------------------------------------------------
   Group means (n per group = 30):
     control      mean = 18.73
     cbt          mean = 14.91
     mindfulness  mean = 12.32

   ANOVA table:
     SS_between = 1235.48, df_between = 2, MS_between = 617.74
     SS_within  = 6710.26, df_within  = 87, MS_within  = 77.01
     SS_total   = 7945.74, df_total   = 89
     F(2, 87) = 8.02, p = 0.0006
     eta^2 = 0.16

   Pairwise comparisons (Bonferroni-corrected p-values):
     control vs cbt:          t(58) = 1.98, p_unc = 0.052, p_bonf = 0.155
     control vs mindfulness:  t(58) = 3.63, p_unc = 0.001, p_bonf = 0.004
     cbt vs mindfulness:      t(58) = 1.65, p_unc = 0.104, p_bonf = 0.312

   SciPy check: f_oneway F = 8.02, p = 0.0006

Focus on:

* **Group means**: Which condition appears best (lowest stress) in raw units?
* **F and p**: Does the overall ANOVA reject :math:`H_0` that all means are
  equal?
* **eta-squared**: How much of the variance in stress scores is explained by
  condition?
* **Post-hoc tests**: Which specific pairs of conditions differ once we control
  for multiple comparisons?

Your Turn: Practice Scenarios
-----------------------------

As in earlier chapters, you can experiment by editing the parameters in
``psych_ch12_one_way_anova.py``:

* **Change the group means**

  Make the three conditions more or less separated. How does this affect
  :math:`F`, :math:`p`, :math:`\eta^2`, and the pairwise tests?

* **Change the group sizes**

  Use unequal group sizes (for example, 20, 30, 40). How does this affect
  the sums of squares and degrees of freedom? What happens if you also make
  the group variances very different—does the equal-variance assumption still
  seem reasonable?

* **Change the within-group variability**

  Increase the group standard deviations. Watch how :math:`MS_{\text{Within}}`
  grows, making the *F*-ratio smaller for the same difference in means.

* **Compare Bonferroni with your intuition**

  Look at uncorrected *p*-values vs. Bonferroni-adjusted *p*-values. Do some
  pairwise differences lose significance after correction? Why is that a
  *feature*, not a bug, from the perspective of Type I error control?

Summary
-------

In this chapter you learned:

* why running many separate *t*-tests can inflate the family-wise Type I error
  rate,
* how one-way ANOVA partitions variability into between-groups and within-groups
  components,
* how to compute and interpret the *F*-ratio and its *p*-value under the
  equal-variance assumption,
* how to quantify effect size using :math:`\eta^2` (and why it is slightly
  biased upward as an estimate of the population effect),
* why post-hoc tests are needed after a significant *F* and how Bonferroni
  correction works in simple pairwise comparisons,
* how to implement a one-way ANOVA and Bonferroni-corrected post-hoc tests
  using PyStatsV1, with a SciPy-based safety check.

In the bigger arc:

* Chapter 10 introduced independent-samples *t*-tests for two groups.
* Chapter 11 introduced paired-samples *t*-tests for within-subjects designs.
* Chapter 12 generalizes the **between-subjects** logic to **three or more
  groups** using ANOVA.

In the next chapter, you will extend these ideas further to **factorial
designs**, where more than one independent variable is manipulated at the same
time.

Code listing
------------

For reference, the full implementation is included via Sphinx:

.. literalinclude:: ../scripts/psych_ch12_one_way_anova.py
   :language: python
   :linenos:
   :caption: ``scripts/psych_ch12_one_way_anova.py`` – simulator and one-way ANOVA helpers
