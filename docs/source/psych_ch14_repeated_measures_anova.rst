Chapter 14 – Repeated-Measures ANOVA
====================================

In Chapters 10–13 you learned how to compare groups when each participant
contributes **one** score per condition:

* independent-samples *t*-tests for two groups (between-subjects),
* paired-samples *t*-tests for two time points or matched pairs,
* one-way ANOVA for three or more independent groups,
* two-way ANOVA for factorial designs with two between-subjects factors.

In many psychology studies, however, we repeatedly measure **the same**
participants over time or across conditions. Examples include:

* stress measured **before**, **after**, and **one month after** a training
  program,
* memory performance under **low**, **medium**, and **high** distraction,
* mood ratings at **multiple time points** during a therapy course.

These are **repeated-measures** (within-subjects) designs with **three or more
levels** of a within-subject factor (often called ``time`` or ``condition``).

In this chapter you will:

* understand the logic of repeated-measures designs,
* see how the ANOVA is adapted to handle **correlated** observations,
* learn how the total variability is partitioned into **subjects**, **time**,
  and **residual** components,
* understand the **sphericity** assumption and why it matters,
* appreciate why repeated-measures designs often have **more power** than
  between-subjects designs, and
* run and interpret a simple repeated-measures ANOVA using PyStatsV1 on a
  balanced design with three time points.

Design Logic: Following the Same People Over Time
-------------------------------------------------

Suppose a clinical psychologist evaluates a stress-management program. Each
participant completes a stress questionnaire at three time points:

* ``pre`` – before training,
* ``post`` – immediately after training,
* ``followup`` – one month later.

The outcome variable is a continuous ``stress_score`` (higher = more stress).
Every participant contributes **three scores**. The research question is:

*Does mean stress change over time?*

A naïve approach would be to run multiple paired-samples *t*-tests:

* pre vs post,
* post vs followup,
* pre vs followup.

As in Chapter 12, this would inflate the **family-wise** Type I error rate.
Instead, we use a **repeated-measures ANOVA** with a single within-subject
factor ``time`` (three levels: pre, post, followup).

Key design features:

* Each participant is measured at **all** levels of the factor.
* Scores within a participant are **correlated** (same person, same traits).
* We can separate variability due to **stable individual differences** from
  variability due to **time** and random noise.

Why Not Just Treat It as a One-Way ANOVA?
-----------------------------------------

If we ignored the repeated-measures nature of the design and treated the
three time points as independent groups, we would:

* violate the independence assumption,
* **underestimate** the standard errors (because we pretend repeated scores
  are independent when they are not),
* inflate the Type I error rate.

Repeated-measures ANOVA explicitly accounts for the fact that observations
within a person are correlated. The basic idea is to give each participant
their **own baseline** and then focus on **how they change over time**.

Partitioning Variance in the Repeated-Measures ANOVA
----------------------------------------------------

In Chapter 12 (one-way ANOVA) we partitioned the total variability into:

* between-groups variability (signal), and
* within-groups variability (noise).

In the repeated-measures design with one within-subject factor (Time), the
picture is slightly more complex. Let

* :math:`Y_{it}` be the stress score for participant :math:`i` at time
  :math:`t` (pre, post, followup),
* :math:`\bar{Y}_{i\cdot}` be the mean for participant :math:`i` across time,
* :math:`\bar{Y}_{\cdot t}` be the mean at time :math:`t` across participants,
* :math:`\bar{Y}_{\cdot\cdot}` be the grand mean (all participants, all times).

We start with the total sum of squares:

.. math::

   SS_{\text{Total}} =
   \sum_i \sum_t (Y_{it} - \bar{Y}_{\cdot\cdot})^2.

This can be decomposed into two major parts:

.. math::

   SS_{\text{Total}} = SS_{\text{Subjects}} + SS_{\text{Within}},

where:

* :math:`SS_{\text{Subjects}}` measures stable differences between
  participants (some people are generally more stressed than others),
* :math:`SS_{\text{Within}}` captures variability **within** participants
  across time points.

The within-participants portion is then further decomposed into:

.. math::

   SS_{\text{Within}} = SS_{\text{Time}} + SS_{\text{Residual}},

where:

* :math:`SS_{\text{Time}}` reflects systematic changes in the mean stress
  score over time (our effect of interest),
* :math:`SS_{\text{Residual}}` captures the leftover, unsystematic variability
  (error) after accounting for subject and time effects.

**Note the difference from Chapter 12.** In a between-subjects one-way ANOVA,
the *error* term includes **all** individual differences. In the
repeated-measures ANOVA, we explicitly separate out those individual
differences into :math:`SS_{\text{Subjects}}` and remove them from the error
term (:math:`SS_{\text{Residual}}`). This reduction in error variance is the
main reason repeated-measures designs are often **more powerful**.

Degrees of Freedom and F-Test for Time
--------------------------------------

If there are :math:`N` participants and :math:`k` time points (for example,
:math:`k = 3` for pre, post, followup), then:

* Total degrees of freedom:

  .. math::

     df_{\text{Total}} = Nk - 1.

* Subjects degrees of freedom:

  .. math::

     df_{\text{Subjects}} = N - 1.

* Within-subjects degrees of freedom:

  .. math::

     df_{\text{Within}} = (N - 1)(k - 1).

* Time degrees of freedom:

  .. math::

     df_{\text{Time}} = k - 1.

* Residual (error) degrees of freedom:

  .. math::

     df_{\text{Residual}} = (N - 1)(k - 1).

We convert sums of squares to mean squares in the usual way:

.. math::

   MS_{\text{Time}} =
   \frac{SS_{\text{Time}}}{df_{\text{Time}}}, \quad
   MS_{\text{Residual}} =
   \frac{SS_{\text{Residual}}}{df_{\text{Residual}}}.

The F-statistic for the Time effect is then:

.. math::

   F_{\text{Time}} = \frac{MS_{\text{Time}}}{MS_{\text{Residual}}}.

Under the null hypothesis that the population means at all time points are
equal,

.. math::

   H_0 : \mu_{\text{pre}} = \mu_{\text{post}} = \mu_{\text{followup}},

the F-statistic follows an F distribution with

* :math:`df_1 = df_{\text{Time}} = k - 1` in the numerator, and
* :math:`df_2 = df_{\text{Residual}} = (N - 1)(k - 1)` in the denominator.

Effect Sizes
------------

A common effect size for repeated-measures ANOVA is **eta-squared** for the
Time effect:

.. math::

   \eta^2_{\text{Time}} =
   \frac{SS_{\text{Time}}}{SS_{\text{Total}}}.

This represents the **proportion of total variance** in the outcome that can
be attributed to the Time factor.

As before, :math:`\eta^2` tends to slightly overestimate the population effect
size, especially for small samples. In professional work, researchers often
report **partial eta-squared** or alternative measures, but for introductory
purposes :math:`\eta^2_{\text{Time}}` is a useful summary.

The Sphericity Assumption
-------------------------

Repeated-measures ANOVA relies on all of the usual assumptions
(independence, approximate Normality), plus a **new one** called
**sphericity**.

Intuitively, **sphericity** means that the variability of the **difference
scores** between any pair of time points is roughly the same. Formally, for
three time points (pre, post, followup), sphericity requires that:

* the variance of (pre – post),
* the variance of (pre – followup), and
* the variance of (post – followup)

are approximately equal in the population.

If sphericity is badly violated, the standard F-test for Time becomes too
liberal (Type I error rate is higher than advertised). To correct for this,
many statistical packages apply **epsilon corrections** that reduce the
effective degrees of freedom. Two common choices are:

* **Greenhouse–Geisser** correction,
* **Huynh–Feldt** correction.

.. admonition:: Professional Tip: Sphericity vs. Compound Symmetry

   Some textbooks talk about **compound symmetry** (equal variances and equal
   covariances across time). Compound symmetry is a **stronger** condition
   than sphericity. Sphericity is the true requirement for the standard
   repeated-measures F-test, and it can hold even when compound symmetry does
   not.

   In practice, many researchers rely on software which automatically checks
   sphericity (for example, with Mauchly’s test) and applies Greenhouse–Geisser
   or Huynh–Feldt corrections as needed.

.. admonition:: Our Approach in PyStatsV1

   In this mini-book we focus on **balanced, well-behaved designs** where
   sphericity is a reasonable approximation. The PyStatsV1 Chapter 14 helpers
   implement the *classical* repeated-measures ANOVA for a single within-subject
   factor with equal :math:`n` at each time point.

   For real research projects, you should use dedicated libraries that
   implement sphericity checks and corrections automatically. In Python,
   two especially useful tools are:

   * :mod:`pingouin` – a user-friendly statistics package for psychology,
     including :func:`pingouin.rm_anova` for repeated-measures ANOVA;
   * :mod:`statsmodels` – a general-purpose modeling library that supports
     repeated-measures and mixed models via formulas.

   These tools also encourage you to think in a **data-science style**:
   reshaping datasets from "wide" (one column per time point) to "long" (one
   row per person–time combination with columns like ``subject``, ``time``,
   and ``score``), which is the standard in modern statistical computing.

Advantages and Trade-Offs of Repeated-Measures Designs
------------------------------------------------------

Advantages:

* **Higher statistical power**

  By removing stable individual differences from the error term, we often get
  much more precise estimates of the Time effect.

* **Fewer participants required**

  Measuring each participant multiple times can achieve the same precision
  with a smaller sample than a comparable between-subjects design.

* **Focus on change**

  Repeated-measures designs naturally answer questions about trajectories:
  improvement, decline, adaptation, and so on.

Trade-offs and challenges:

* **Carryover effects**

  Experience in earlier conditions can influence later responses (for example,
  practice, fatigue, or learning).

* **Order effects**

  The order of conditions matters. Researchers use techniques like
  counterbalancing or randomization to mitigate this.

* **Missing data complexity**

  If some participants miss a time point, analysis becomes more complex.
  Modern mixed-effects models (see Chapter 17) are often better suited for
  heavily unbalanced longitudinal data.

PyStatsV1 Lab: Repeated-Measures ANOVA on Stress Over Time
----------------------------------------------------------

In the Chapter 14 lab, you will analyze a simulated repeated-measures study
of stress scores at three time points:

* ``pre`` – before a training program,
* ``post`` – immediately after training,
* ``followup`` – one month later.

The design assumes:

* :math:`N` participants (for example, 40),
* all participants measured at all three time points (balanced design),
* modest decreases in stress from pre → post and post → followup.

You will:

* simulate a balanced repeated-measures dataset with columns like
  ``subject_id``, ``time`` (pre/post/followup), and ``stress_score``,
* compute:

  - means and standard deviations for each time point,
  - sums of squares :math:`SS_{\text{Total}}`, :math:`SS_{\text{Subjects}}`,
    :math:`SS_{\text{Within}}`, :math:`SS_{\text{Time}}`,
    :math:`SS_{\text{Residual}}`,
  - the corresponding degrees of freedom and mean squares,
  - the F-statistic and *p*-value for the Time effect,
  - :math:`\eta^2_{\text{Time}}` as an effect size,

* produce a simple **line plot** of mean stress over time with error bars,
* optionally run pairwise comparisons (for example, pre vs post, post vs
  followup) with Bonferroni-adjusted *p*-values,
* optionally cross-check the ANOVA results against :func:`pingouin.rm_anova`
  if the :mod:`pingouin` package is installed.

All code for this lab lives in:

* ``scripts/psych_ch14_repeated_measures_anova.py``

and the script can optionally write outputs to:

* ``data/synthetic/psych_ch14_repeated_stress.csv``

Running the Lab Script
----------------------

From the project root, you can run:

.. code-block:: bash

   python -m scripts.psych_ch14_repeated_measures_anova

If your Makefile defines a convenience target, you can instead run:

.. code-block:: bash

   make psych-ch14

This will:

* simulate a balanced repeated-measures dataset,
* print descriptive statistics for each time point,
* compute the repeated-measures ANOVA table (Time effect),
* report :math:`\eta^2_{\text{Time}}`,
* draw (or save) a line plot of mean stress over time with error bars,
* optionally print pairwise comparisons and, if available,
  a :mod:`pingouin`-based check of the ANOVA results.

Expected Console Output
-----------------------

Your exact numbers will vary if you change the seed or parameters, but with
the default settings you might see output like:

.. code-block:: text

   Repeated-measures ANOVA on stress scores (Time: pre, post, followup)
   --------------------------------------------------------------------
   Descriptive stats by time:
     pre:      mean = 22.4, sd = 4.9,  n = 40
     post:     mean = 18.5, sd = 4.6,  n = 40
     followup: mean = 17.1, sd = 4.8,  n = 40

   ANOVA table (within-subjects factor: Time)
     SS_Total      =  4752.39, df_Total      = 119
     SS_Subjects   =  3180.12, df_Subjects   =  39
     SS_Within     =  1572.27, df_Within     =  80
     SS_Time       =   892.54, df_Time       =   2
     SS_Residual   =   679.73, df_Residual   =  78

     MS_Time       =   446.27
     MS_Residual   =     8.71
     F_Time(2, 78) =   51.23, p < 0.001
     eta^2_Time    =   0.19

   Pairwise comparisons (Bonferroni-adjusted p-values):
     pre vs post:      t(39) =  7.10, p_bonf < 0.001
     post vs followup: t(39) =  2.60, p_bonf = 0.036
     pre vs followup:  t(39) =  8.40, p_bonf < 0.001

   (Optional) Pingouin check:
     rm_anova F = 51.25, p < 0.001, np2 = 0.19

   Plot saved to: outputs/track_b/ch14_stress_over_time.png

Focus on:

* **Mean trends**: Do the line plot and descriptives show clear improvement
  over time?
* **ANOVA result**: Does the F-test for Time indicate a statistically
  significant change in mean stress?
* **Effect size**: Is :math:`\eta^2_{\text{Time}}` small, medium, or large in
  your field’s context?
* **Pairwise comparisons**: Which specific time intervals show reliable
  change after correcting for multiple tests?

Your Turn: Practice Scenarios
-----------------------------

As in earlier chapters, you can experiment by editing parameters in
``psych_ch14_repeated_measures_anova.py``. Some ideas:

* **Change the mean trajectory**

  Make stress drop sharply from pre to post and then stay flat, or include a
  slight rebound at followup. How does this affect the F-test and pairwise
  comparisons?

* **Change the within-person variability**

  Increase or decrease the standard deviation of the noise term. Watch how
  :math:`MS_{\text{Residual}}` changes and how that affects the F-statistic.

* **Compare to multiple paired *t*-tests**

  Manually run paired *t*-tests for pre vs post, post vs followup, and pre vs
  followup. How do their *p*-values compare to the global ANOVA test when you
  correct for multiple comparisons?

* **Experiment with the sample size**

  Try :math:`N = 20` vs :math:`N = 80`. How does the power (sensitivity) of
  the test change? Can you see smaller effects with larger samples?

Summary
-------

In this chapter you learned:

* how repeated-measures designs follow the **same participants** across three
  or more time points or conditions,
* how repeated-measures ANOVA partitions total variability into **subjects**,
  **time**, and **residual** components,
* why removing stable individual differences from the error term increases
  **statistical power**,
* what the **sphericity** assumption is and why epsilon corrections
  (Greenhouse–Geisser, Huynh–Feldt) are used in professional software,
* how to implement a simple repeated-measures ANOVA in PyStatsV1 for a
  balanced design, and how to visualize trajectories over time,
* how modern Python tools like :mod:`pingouin` and :mod:`statsmodels` support
  more advanced repeated-measures and mixed-model analyses in a
  data-science-friendly workflow (long-format data, formula syntax).

In the bigger arc:

* Chapter 11 introduced paired-samples *t*-tests for two time points.
* Chapter 12 extended the logic to multiple independent groups via one-way
  ANOVA.
* Chapter 13 introduced factorial designs and two-way ANOVA for multiple
  between-subjects factors.
* Chapter 14 takes the next step to **within-subjects ANOVA** for three or
  more time points on the same participants.

In Chapter 17, you will see how these ideas generalize further to
**mixed-model designs**, where within-subjects (repeated) factors and
between-subjects factors are analyzed together in a unified framework.

For the full Python implementation, see
``scripts/psych_ch14_repeated_measures_anova.py`` in the PyStatsV1 GitHub
repository.
