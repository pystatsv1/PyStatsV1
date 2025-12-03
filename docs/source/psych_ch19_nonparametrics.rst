==============================
Chapter 19 – Non-Parametric Statistics
==============================

Learning goals
==============

By the end of this chapter you will be able to:

* Explain when non-parametric tests are preferred over traditional (parametric)
  procedures such as the *t*-test or ANOVA.
* Describe the logic of the chi-square family of tests.
* Distinguish between chi-square tests of **goodness of fit** and
  **independence**.
* Recognize rank-based alternatives to *t*-tests and one-way ANOVA
  (Mann–Whitney U, Wilcoxon signed-rank, Kruskal–Wallis, Friedman).
* Use :mod:`PyStatsV1` and :mod:`pingouin` to analyze survey-style data
  with chi-square tests on categorical variables.

19.1 When parametric assumptions break down
===========================================

In earlier chapters, we focused on *parametric* procedures:

* *t*-tests (Chapters 9–11)
* One-way and factorial ANOVA (Chapters 12–14)
* Regression and ANCOVA (Chapters 16–18)

These procedures make several assumptions about the data:

* **Quantitative scale** – variables are interval or ratio, not purely nominal.
* **Normality** – scores within each group are (approximately) normally
  distributed.
* **Homogeneity of variance** – population variances are equal across groups.
* **Linearity** – for correlation and regression, the relationship between
  variables is approximately linear.

When these assumptions are badly violated, parametric tests can give
misleading *p*-values and confidence intervals. In those cases, we often turn
to **non-parametric** methods.

Non-parametric tests typically:

* Work with **ranks** or **counts** rather than raw numeric values.
* Make **fewer distributional assumptions**.
* Are often slightly **less powerful** when parametric assumptions *are* met,
  but **more robust** when those assumptions fail.

In psychological research, non-parametric tests are especially useful when:

* The outcome is **ordinal** (e.g., Likert scales: “Strongly disagree” to
  “Strongly agree”).
* The data are **severely skewed** or have heavy **outliers** that cannot be
  reasonably transformed.
* The variable is **categorical** (e.g., therapy preference, diagnostic
  category, treatment response yes/no).

19.2 Chi-square tests for categorical data
==========================================

The most common non-parametric tests in introductory psychology involve
**frequency counts** in categories. The basic question is:

    *Do the observed counts differ from what we would expect by chance?*

The chi-square family addresses this question in two main situations.

19.2.1 Goodness of fit
----------------------

A **chi-square goodness-of-fit test** compares observed category counts to
a theoretical or expected distribution. For example:

* A survey asks which coping strategy students use most often:
  *Exercise*, *Therapy*, *Mindfulness*, or *Social support*.
* If there was **no preference**, we would expect roughly equal counts in each
  category (25% each).
* The chi-square goodness-of-fit test asks whether the observed distribution
  differs significantly from this uniform expectation.

Statistically, we compute::

    χ² = Σ (Observed - Expected)² / Expected

with degrees of freedom :math:`df = k - 1`, where *k* is the number of
categories.

If χ² is large relative to its degrees of freedom, the *p*-value will be small
and we reject the null hypothesis that the observed frequencies match the
expected distribution.

19.2.2 Test of independence
---------------------------

A **chi-square test of independence** asks whether two categorical variables
are related. For example:

* Variable 1: Type of therapy received (*Control*, *CBT*, *Mindfulness*).
* Variable 2: Treatment outcome (*Improved* vs. *Did not improve*).

We arrange the counts in a **contingency table** and again compute a chi-square
statistic. Here, the null hypothesis states that the variables are **independent** –
knowing a person’s therapy type tells you nothing about their likelihood of
improvement.

We also report an **effect size** such as **Cramér’s V**, which is based on
the chi-square value but scaled to lie between 0 and 1:

* ~0.10: small association
* ~0.30: medium
* ~0.50 or higher: large

19.3 Rank-based tests
=====================

Not all non-parametric tests are based on counts. Many are based on **ranks**
of the outcome variable. Instead of analyzing raw scores, we:

1. Combine all scores across groups.
2. Rank them from lowest to highest.
3. Analyze the ranks using an appropriate test statistic.

Some common rank-based tests and their parametric counterparts:

* **Mann–Whitney U**: alternative to an independent-samples *t*-test.
* **Wilcoxon signed-rank**: alternative to a paired-samples *t*-test.
* **Kruskal–Wallis H**: alternative to a one-way ANOVA with independent groups.
* **Friedman test**: alternative to a repeated-measures one-way ANOVA.

These tests are especially helpful when:

* The outcome is ordinal (e.g., 1–7 rating scales).
* The data are heavily skewed or contain extreme outliers.
* Sample sizes are small, making normality assumptions doubtful.

19.4 When to choose non-parametric methods
==========================================

There is no single “magic rule,” but some practical guidelines:

* **Use chi-square tests** when both your predictor and outcome are
  **categorical** (nominal) and you are working with **counts**, not
  percentages.
* **Use rank-based tests** when:
  * The outcome variable is **ordinal**, or
  * You have strong violations of normality or homogeneity that cannot be
    fixed by transformations, and
  * You are more concerned about **validity** than about squeezing out every
    bit of statistical **power**.

When in doubt, you can often:

* Run the **parametric** test (e.g., *t*-test or ANOVA).
* Run the **non-parametric** alternative.
* Compare conclusions – if they agree, your result is probably robust.

19.5 PyStatsV1 Lab: Chi-square analysis of survey data
======================================================

In this chapter’s lab you will use :mod:`PyStatsV1` to analyze **simulated
survey data** using chi-square tests. The code lives in:

* :mod:`scripts.psych_ch19_nonparametrics`
* :mod:`tests.test_psych_ch19_nonparametrics`

Running the lab
----------------

From the project root (with your virtual environment activated), run::

    make psych-ch19
    make test-psych-ch19

The first command will:

1. Simulate a **coping strategies** survey with four categories
   (e.g., Exercise, Therapy, Mindfulness, Social support).
2. Run a **chi-square goodness-of-fit** test to check whether the observed
   distribution differs from a uniform (no-preference) null.
3. Save the raw data and a summary table to:

   * ``data/synthetic/psych_ch19_survey_gof.csv``
   * ``outputs/track_b/ch19_gof_table.csv``

4. Generate a bar chart comparing **observed** versus **expected** counts:

   * ``outputs/track_b/ch19_gof_barplot.png``

The second dataset in the script simulates a **therapy × improvement**
contingency table:

1. Students are randomly assigned to *Control*, *CBT*, or *Mindfulness*
   conditions.
2. Each person is classified as *Improved* or *No change*.
3. The script uses:

   * :func:`scipy.stats.chi2_contingency` for a traditional chi-square test.
   * :func:`pingouin.chi2_independence` to obtain effect sizes
     (e.g., Cramér’s V) and power estimates.

4. The script saves:

   * ``data/synthetic/psych_ch19_survey_independence.csv`` – individual-level data.
   * ``outputs/track_b/ch19_independence_table.csv`` – full chi-square summary.
   * ``outputs/track_b/ch19_stacked_bar.png`` – a stacked bar plot showing the
     proportion improved within each therapy type.

Interpreting the output
------------------------

After running ``make psych-ch19``, inspect the console output and figures:

* For the **goodness-of-fit** example, ask:

  * Does the chi-square test detect that some coping strategies are preferred
    over others?
  * Which categories contribute most to the chi-square statistic (largest
    observed – expected differences)?

* For the **independence** example, ask:

  * Is there evidence that treatment type and improvement are associated?
  * How large is the association (Cramér’s V)?
  * Do the stacked bar plots reveal a pattern that matches the numerical
    results?

Connection to earlier chapters
------------------------------

This chapter ties together several themes from earlier in the book:

* Just as in Chapter 7, we rely on **sampling distributions** to interpret
  chi-square statistics.
* As in Chapters 9–12, we balance **Type I error** (false positives) against
  **power** (true positives).
* In Chapters 16–18, we extended ANOVA to regression and ANCOVA. Here, we
  extend the logic of hypothesis testing to **categorical outcomes** and
  **ordinal data**.

Non-parametric methods are not a separate universe – they are another set of
tools in your scientific toolbox. When used thoughtfully, they allow you to
test important psychological questions even when real-world data refuse to
behave “nicely.”
