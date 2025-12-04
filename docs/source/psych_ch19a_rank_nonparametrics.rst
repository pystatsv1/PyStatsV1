
.. _psych_ch19a_rank_nonparametrics:

Chapter 19a – Rank-Based Non-Parametric Alternatives
====================================================

Where this chapter fits in the story
------------------------------------

In :strong:`Chapter 10–12` you met the classic parametric workhorses:

* Independent-samples :math:`t` test (Chapter 10)
* Paired-samples :math:`t` test (Chapter 11)
* One-way ANOVA (Chapter 12)

In :strong:`Chapter 19` you stepped into a different world: categorical outcomes,
contingency tables, and :math:`\chi^2` tests (goodness-of-fit and independence).
Those procedures are designed for **counts in categories**.

This appendix, Chapter 19a, fills in the missing bridge:

*What do we do when our outcome is still a continuous score (like stress, reaction time,
or exam performance), but the assumptions of :math:`t` and ANOVA are badly violated?*

That is the home territory of **rank-based non-parametric tests.** They keep the
basic research questions from Chapters 10–12 but answer them using **ranks instead
of raw scores.**


When to reach for rank-based tests
----------------------------------

Rank-based tests are especially useful when:

* Your outcome is **ordinal** or strongly **skewed** (e.g., reaction times, income,
  symptom counts).
* You have **outliers** that are hard to justify removing, and transformations do
  not fully fix the problem.
* Your sample sizes are moderate or small, and normal-theory approximations for
  :math:`t` and :math:`F` are questionable.

They are still asking the *same substantive questions* as the parametric tests:

* Is there a difference between two independent groups?
* Is there a difference between two paired conditions (e.g., pre vs. post)?
* Are there differences among three or more groups?

But instead of modeling the **mean** of a (roughly) normal distribution, they work
with **ranks** and use test statistics that are robust to shape and outliers.


Mann–Whitney U: Alternative to an independent-samples t test
------------------------------------------------------------

Recall the independent-samples :math:`t` test from Chapter 10:

* Two independent groups (e.g., Control vs. Treatment)
* Approximately normal scores within each group
* Roughly equal variances

The :strong:`Mann–Whitney U` test answers a similar question using ranks. Instead of
comparing group means, it asks whether scores in one group tend to be **larger**
than scores in the other group.

Key ideas:

* Combine all scores from both groups, rank them from lowest to highest.
* Compute a statistic :math:`U` that reflects how often one group has higher ranks
  than the other.
* Under the null hypothesis (no difference), rank patterns are similar between groups.

In the lab script :mod:`scripts.psych_ch19a_rank_nonparametrics`, we:

* Simulate a continuous, **skewed** outcome for Control and Treatment.
* Run :func:`pingouin.mwu` to obtain :math:`U`, :math:`p`, and an effect size (rank-biserial correlation).
* Visualize the distribution with boxplots to highlight skew and overlap.


Wilcoxon signed-rank: Alternative to a paired-samples t test
------------------------------------------------------------

In Chapter 11, the paired-samples :math:`t` test analyzed **difference scores**
(e.g., Post – Pre) under the assumption that those differences were roughly normal.

The :strong:`Wilcoxon signed-rank` test keeps the same design (paired data), but:

* Works with the **ranks of absolute differences** instead of the raw differences.
* Uses the signs (+/-) to capture direction (improvement vs. decline).

It is especially useful when:

* Individual differences are large.
* Change scores are asymmetric or have outliers (e.g., a few participants improve *a lot*).

In the lab script we:

* Simulate Pre vs. Post scores with a **positive shift** plus skew and noise.
* Run :func:`pingouin.wilcoxon` on the paired data.
* Confirm that Wilcoxon detects the systematic shift, even when parametric assumptions
  are dubious.


Kruskal–Wallis: Alternative to one-way ANOVA
--------------------------------------------

The one-way ANOVA from Chapter 12 extends the independent-samples :math:`t` test
to three or more groups, comparing **means** via an :math:`F` statistic.

The :strong:`Kruskal–Wallis` test is its rank-based cousin:

* Combine all group scores and rank them.
* Compute a statistic :math:`H` that reflects how far each group’s **mean rank**
  is from the overall mean rank.
* Under the null hypothesis, all groups have similar rank distributions.

In the lab script we:

* Simulate a three-group dose example (Low, Medium, High) with positively skewed scores.
* Run :func:`pingouin.kruskal` to test for any group differences.
* Confirm that the Kruskal–Wallis test recovers the intended order of group effects.


PyStatsV1 Lab: Rank-based non-parametric tests in action
--------------------------------------------------------

The Chapter 19a lab is implemented in:

* :mod:`scripts.psych_ch19a_rank_nonparametrics`
* :mod:`tests.test_psych_ch19a_rank_nonparametrics`

The script does three things:

1. :strong:`Mann–Whitney U demo`

   * Simulates skewed scores for Control vs. Treatment.
   * Runs :func:`pingouin.mwu` and prints the :math:`U` statistic, :math:`p` value,
     and effect size.
   * Saves the simulated dataset to:

     * :file:`data/synthetic/psych_ch19a_mannwhitney_demo.csv`

   * Saves the test results to:

     * :file:`outputs/track_b/ch19a_mannwhitney_results.csv`

2. :strong:`Wilcoxon signed-rank demo`

   * Simulates Pre vs. Post scores for the same participants.
   * Runs :func:`pingouin.wilcoxon` on the paired data.
   * Saves the wide-format data (one row per participant) to:

     * :file:`data/synthetic/psych_ch19a_wilcoxon_demo.csv`

   * Saves the test results to:

     * :file:`outputs/track_b/ch19a_wilcoxon_results.csv`

3. :strong:`Kruskal–Wallis demo`

   * Simulates a three-group design (e.g., Low / Medium / High dosing).
   * Runs :func:`pingouin.kruskal` to test for differences among groups.
   * Saves the dataset to:

     * :file:`data/synthetic/psych_ch19a_kruskal_demo.csv`

   * Saves the test results to:

     * :file:`outputs/track_b/ch19a_kruskal_results.csv`

Finally, the script creates a small figure comparing group distributions (via boxplots)
and saves it as:

* :file:`outputs/track_b/ch19a_rank_nonparam_boxplots.png`


Running the Chapter 19a lab
---------------------------

From the project root, you can run the full demo with::

   make psych-ch19a

To run only the tests for this chapter::

   make test-psych-ch19a

These targets simply wrap:

* :command:`python -m scripts.psych_ch19a_rank_nonparametrics`
* :command:`pytest tests/test_psych_ch19a_rank_nonparametrics.py`


Conceptual summary
------------------

* Chapter 19 (chi-square) focused on **categorical outcomes** and counts in categories.
* Chapter 19a (this appendix) focuses on **continuous / ordinal outcomes** where
  parametric assumptions are shaky.

Rank-based non-parametric tests:

* Keep the :emphasis:`research questions` from your t-tests and ANOVAs.
* Answer them using **ranks** and robust test statistics instead of relying on
  normality of raw scores.
* Provide a practical toolset when data are messy, skewed, or resistant to transformation.

In more advanced courses (e.g., Robust Methods, Categorical Data Analysis, or
Generalized Linear Models), you will see how these ideas generalize further:
logistic regression for categorical outcomes, robust regression for outliers,
and permutation tests for flexible, assumption-lean inference.

For now, Chapter 19a gives you a principled way to say:

*“Even when the assumptions of t and ANOVA are not met, I can still design and
analyze my study using methods that respect the structure of my data.”*
